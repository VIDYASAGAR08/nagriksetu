import io
import os
import re
import string
from typing import Dict, Any, Tuple, Optional

# Dependencies installed in container
try:
    from PIL import Image, ImageEnhance, ImageFilter
    import pytesseract
    from pytesseract import Output
    HAS_TESSERACT = True
except Exception:
    HAS_TESSERACT = False

try:
    import pypdf
    HAS_PYPDF = True
except Exception:
    HAS_PYPDF = False


def preprocess_image(image_bytes: bytes) -> "Image.Image":
    """
    Applies image preprocessing:
    - Load via Pillow
    - Grayscale conversion
    - Contrast enhancement
    - Median filter for noise reduction
    """
    img = Image.open(io.BytesIO(image_bytes))
    # Grayscale
    gray = img.convert("L")
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(gray)
    contrast = enhancer.enhance(1.8)
    # Slight sharpening
    sharp = contrast.filter(ImageFilter.SHARPEN)
    return sharp


def extract_text_from_pdf(file_path: str) -> Tuple[str, float]:
    """
    Extracts text from PDF file using pypdf.
    Returns (raw_text, confidence_score).
    """
    if not HAS_PYPDF or not os.path.exists(file_path):
        return "", 0.0

    try:
        reader = pypdf.PdfReader(file_path)
        full_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text.append(t)
        text = "\n".join(full_text).strip()
        confidence = 95.0 if len(text) > 20 else 70.0
        return text, confidence
    except Exception as e:
        return "", 0.0


def extract_text_and_confidence_from_image(file_path: str) -> Tuple[str, float]:
    """
    Runs Tesseract OCR on preprocessed image.
    Calculates actual average confidence score from word confidences.
    """
    if not HAS_TESSERACT or not os.path.exists(file_path):
        return "", 0.0

    try:
        with open(file_path, "rb") as f:
            img_bytes = f.read()

        processed_img = preprocess_image(img_bytes)
        ocr_data = pytesseract.image_to_data(processed_img, output_type=Output.DICT)

        words = []
        confidences = []
        for i, word in enumerate(ocr_data["text"]):
            w = word.strip()
            conf = float(ocr_data["conf"][i])
            if w and conf > 0:
                words.append(w)
                confidences.append(conf)

        raw_text = " ".join(words)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        return raw_text, round(avg_conf, 1)
    except Exception as e:
        return "", 0.0


def parse_structured_entities(text: str) -> Dict[str, Any]:
    """
    Rule and regex grounded entity extraction for educational certificates:
    - Candidate Name
    - Date of Birth
    - Registration / TC / Certificate Number
    - Marks / Percentage
    - Issuing Authority
    """
    entities: Dict[str, Any] = {
        "candidate_name": None,
        "date_of_birth": None,
        "registration_number": None,
        "marks_percentage": None,
        "issuing_authority": None
    }

    # 1. Date of Birth Patterns: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
    dob_match = re.search(r"\b(0[1-9]|[12][0-9]|3[01])[-/.](0[1-9]|1[0-2])[-/.](19[89][0-9]|20[0-2][0-9])\b", text)
    if dob_match:
        entities["date_of_birth"] = dob_match.group(0)
    else:
        iso_dob = re.search(r"\b(19[89][0-9]|20[0-2][0-9])[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12][0-9]|3[01])\b", text)
        if iso_dob:
            entities["date_of_birth"] = iso_dob.group(0)

    # 2. Registration / Certificate Number
    reg_match = re.search(r"(?:reg(?:istration)?\s*(?:no|num|number)?|cert(?:ificate)?\s*(?:no|number)?|tc\s*(?:no|number)?|roll\s*(?:no)?|id\s*(?:no)?)\s*[:.-]?\s*([A-Za-z0-9/-]{4,20})", text, re.IGNORECASE)
    if reg_match:
        entities["registration_number"] = reg_match.group(1).strip()

    # 3. Marks / Percentage
    pct_match = re.search(r"(\d{1,2}(?:\.\d{1,2})?)\s*%", text)
    if pct_match:
        entities["marks_percentage"] = float(pct_match.group(1))
    else:
        marks_match = re.search(r"(?:marks|score|total|percentage)\s*[:.-]?\s*(\d{2,3}(?:\.\d{1,2})?)", text, re.IGNORECASE)
        if marks_match:
            try:
                val = float(marks_match.group(1))
                if val <= 100:
                    entities["marks_percentage"] = val
            except Exception:
                pass

    # 4. Candidate Name Extraction
    name_match = re.search(r"(?:name\s*(?:of\s*(?:the)?\s*candidate|of\s*student)?|student\s*name)\s*[:.-]?\s*([A-Za-z\s.]{3,35})", text, re.IGNORECASE)
    if name_match:
        entities["candidate_name"] = name_match.group(1).strip()

    # 5. Issuing Authority
    if re.search(r"karnataka\s*(?:secondary|school|state|board|kseab)", text, re.IGNORECASE):
        entities["issuing_authority"] = "Karnataka School Examination and Assessment Board (KSEAB)"
    elif re.search(r"cbse|central\s*board", text, re.IGNORECASE):
        entities["issuing_authority"] = "Central Board of Secondary Education (CBSE)"
    elif re.search(r"pre[- ]university|pue|dpu", text, re.IGNORECASE):
        entities["issuing_authority"] = "Department of Pre-University Education, Karnataka"
    elif re.search(r"municipal|corporation|registrar\s*of\s*births", text, re.IGNORECASE):
        entities["issuing_authority"] = "Registrar of Births & Deaths, Govt of Karnataka"

    # 6. Standard / Class
    std_match = re.search(r"(?:standard|class|grade|std)\s*[:.-]?\s*(\d{1,2}|[IVXLCDM]+)", text, re.IGNORECASE)
    if std_match:
        entities["standard"] = f"Class {std_match.group(1).strip()}"

    # 7. School / Institution ID
    sch_match = re.search(r"\b((?:SCH|COL)\d{3})\b", text, re.IGNORECASE)
    if sch_match:
        entities["school_id"] = sch_match.group(1).upper()

    # 8. Guardian / Parent Name
    guard_match = re.search(r"(?:father(?:'s)?|mother(?:'s)?|guardian(?:'s)?)\s*(?:name)?\s*[:.-]?\s*([A-Za-z\s.]{3,35})", text, re.IGNORECASE)
    if guard_match:
        entities["guardian_name"] = guard_match.group(1).strip()

    return entities


def compare_and_audit_discrepancies(
    extracted_entities: Dict[str, Any],
    app_applicant_name: Optional[str],
    stage2_dob: Optional[str],
    stage2_marks: Optional[float]
) -> Tuple[str, str]:
    """
    Compares real OCR extracted fields against user submitted Stage 1/2 application data.
    Returns (match_status, discrepancy_notes).
    """
    discrepancies = []
    matches = []

    # Name check
    ocr_name = extracted_entities.get("candidate_name")
    if ocr_name and app_applicant_name:
        # Normalize and compare
        n1 = set(ocr_name.lower().split())
        n2 = set(app_applicant_name.lower().split())
        if n1 & n2:
            matches.append(f"Candidate Name matches: '{ocr_name}' ~ '{app_applicant_name}'")
        else:
            discrepancies.append(f"Name Discrepancy: OCR detected '{ocr_name}', application has '{app_applicant_name}'")

    # DOB check
    ocr_dob = extracted_entities.get("date_of_birth")
    if ocr_dob and stage2_dob:
        clean_ocr_dob = "".join(c for c in ocr_dob if c.isdigit())
        clean_sub_dob = "".join(c for c in stage2_dob if c.isdigit())
        if clean_ocr_dob == clean_sub_dob or clean_ocr_dob[::-1] == clean_sub_dob:
            matches.append(f"DOB verified: {ocr_dob}")
        else:
            # Check year match
            if stage2_dob[:4] in ocr_dob or ocr_dob[-4:] in stage2_dob:
                matches.append(f"DOB year verified: {stage2_dob[:4]}")
            else:
                discrepancies.append(f"DOB Discrepancy: OCR detected '{ocr_dob}', application has '{stage2_dob}'")

    if discrepancies:
        return "discrepancy_detected", " | ".join(discrepancies)
    elif matches:
        return "verified_match", " | ".join(matches)
    else:
        return "unreviewed", "OCR text parsed. Staff visual review required to confirm certificate details."
