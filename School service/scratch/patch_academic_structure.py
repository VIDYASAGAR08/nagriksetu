path = r'C:\Users\callm\nagriksetu\backend\main.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = """            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category_type": "K10_SCHOOL",
                "standards": standards,
                "sections_by_standard": sections_by_std,
                "academic_years": ["2026-2027", "2025-2026"]
            }"""

replacement = """            all_sections = sorted(list({s for secs in sections_by_std.values() for s in secs}))
            if not all_sections:
                all_sections = ["A", "B", "C"]
            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "K10_SCHOOL",
                "standards": standards,
                "sections": all_sections,
                "sections_by_standard": sections_by_std,
                "academic_years": ["2026-2027", "2025-2026"]
            }"""

if target in text:
    text = text.replace(target, replacement)
    print("Patched K10!")
elif target.replace('\n', '\r\n') in text:
    text = text.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'))
    print("Patched K10 CRLF!")
else:
    print("K10 target not found")

target_pu = """            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category_type": "PU_COLLEGE",
                "pu_levels": pu_levels,
                "streams": streams,
                "combinations_by_stream": combinations_by_stream,
                "sections": sections,
                "academic_years": ["2026-2027", "2025-2026"]
            }"""

replacement_pu = """            combo_codes = sorted(list({c["code"] for clist in combinations_by_stream.values() for c in clist if c.get("code")}))
            if not combo_codes:
                combo_codes = ["PCMB", "PCMC", "PCME", "SEBA", "EBAC"]
            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "PU_COLLEGE",
                "pu_levels": pu_levels,
                "streams": streams,
                "combinations": combo_codes,
                "combinations_by_stream": combinations_by_stream,
                "sections": sections,
                "academic_years": ["2026-2027", "2025-2026"]
            }"""

if target_pu in text:
    text = text.replace(target_pu, replacement_pu)
    print("Patched PU!")
elif target_pu.replace('\n', '\r\n') in text:
    text = text.replace(target_pu.replace('\n', '\r\n'), replacement_pu.replace('\n', '\r\n'))
    print("Patched PU CRLF!")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Finished patching academic structure!")
