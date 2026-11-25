"""
NagrikSetu AI Engine - Question Matcher & Intent Classifier
Connects and leverages the 200-question bank in SQLite table `ai_question_bank`.
Handles typos, paraphrased questions, and entity extraction.
"""

import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

COMMON_TYPOS = {
    "skool": "school",
    "shcool": "school",
    "scool": "school",
    "colg": "college",
    "collg": "college",
    "admision": "admission",
    "admisson": "admission",
    "atendance": "attendance",
    "attandance": "attendance",
    "scolarship": "scholarship",
    "scholorship": "scholarship",
    "gov": "government",
    "govt": "government",
    "bangalore": "bengaluru",
    "mysore": "mysuru",
    "mangalore": "mangaluru",
    "standerd": "standard",
    "std": "standard",
    "clas": "class",
    "sub": "subject",
    "subjets": "subjects",
    "transfr": "transfer",
    "techer": "teacher",
    "princpal": "principal",
    "fee": "fees"
}

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or",
    "is", "are", "was", "were", "be", "been", "can", "could", "would",
    "should", "do", "does", "did", "have", "has", "had", "my", "me",
    "i", "you", "your", "we", "our", "it", "its", "what", "which",
    "who", "whom", "where", "when", "why", "how", "please", "tell"
}

class QuestionMatcher:
    def __init__(self):
        self._cached_questions: Optional[List[Dict[str, Any]]] = None

    def _normalize(self, text: str) -> str:
        t = text.lower().strip()
        t = re.sub(r"[^\w\s-]", " ", t)
        words = t.split()
        normalized_words = [COMMON_TYPOS.get(w, w) for w in words]
        return " ".join(normalized_words)

    def _tokenize(self, text: str) -> set:
        normalized = self._normalize(text)
        return {w for w in normalized.split() if w not in STOP_WORDS and len(w) > 1}

    def load_question_bank(self, conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        if self._cached_questions is not None:
            return self._cached_questions

        cursor = conn.cursor()
        rows = cursor.execute("""
            SELECT id, question_code, question_text, category, intended_role,
                   intent, required_information, data_source, answer_method,
                   expected_answer, is_active
            FROM ai_question_bank
            WHERE is_active = 1
            ORDER BY question_code ASC
        """).fetchall()

        questions = []
        for r in rows:
            q_dict = dict(r) if isinstance(r, sqlite3.Row) else {
                "id": r[0], "question_code": r[1], "question_text": r[2],
                "category": r[3], "intended_role": r[4], "intent": r[5],
                "required_information": r[6], "data_source": r[7],
                "answer_method": r[8], "expected_answer": r[9], "is_active": r[10]
            }
            q_dict["tokens"] = self._tokenize(q_dict["question_text"])
            questions.append(q_dict)

        self._cached_questions = questions
        return questions

    def extract_entities(self, text: str, conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
        norm = self._normalize(text)
        entities: Dict[str, Any] = {
            "institution_ids": [],
            "institution_name": None,
            "district": None,
            "standard": None,
            "student_id": None,
            "stream": None
        }

        # Institution IDs like SCH001, COL002
        inst_ids = re.findall(r"\b((?:SCH|COL)\d{3})\b", text, re.IGNORECASE)
        entities["institution_ids"] = [i.upper() for i in list(dict.fromkeys(inst_ids))]

        # Student IDs
        stu_match = re.search(r"\b(STU\d+|PERM\d+|\d{6,10})\b", text, re.IGNORECASE)
        if stu_match:
            entities["student_id"] = stu_match.group(1).upper()

        # Districts in Karnataka
        districts = [
            "bengaluru", "mysuru", "belagavi", "mangaluru", "kalaburagi", "hubballi",
            "dharwad", "shivamogga", "tumakuru", "ballari", "davangere", "vijayapura",
            "hassan", "udupi", "bidar", "hospet", "gadag", "chikkamagaluru", "kolar",
            "mandya", "raichur", "bagalkote", "haveri", "koppal", "yadgir", "chamarajanagar",
            "ramanagara", "chikkaballapura", "kodagu"
        ]
        for dist in districts:
            if dist in norm:
                entities["district"] = dist.capitalize()
                break

        # Standard / Class
        std_match = re.search(r"\b(?:standard|class|std|grade)\s*(\d{1,2}|puc|lkg|ukg)\b", norm)
        if std_match:
            entities["standard"] = std_match.group(1).upper()
        else:
            num_std_match = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)\s*(?:standard|class|std)?\b", norm)
            if num_std_match:
                entities["standard"] = num_std_match.group(1)

        # Streams
        for st in ["science", "commerce", "arts", "humanities", "computer science", "biology"]:
            if st in norm:
                entities["stream"] = st.title()
                break

        # Match institution names from database if conn is provided
        if conn and not entities["institution_ids"]:
            try:
                schools = conn.execute("SELECT school_id, school_name FROM schools").fetchall()
                for sc in schools:
                    s_name = sc["school_name"].lower()
                    if s_name in norm or any(part in norm for part in s_name.split() if len(part) > 4 and part not in ["school", "college", "government", "public", "higher", "secondary"]):
                        entities["institution_ids"].append(sc["school_id"])
                        entities["institution_name"] = sc["school_name"]
                        break
            except Exception:
                pass

        return entities

    def match_question(
        self,
        query: str,
        conn: sqlite3.Connection
    ) -> Tuple[Optional[Dict[str, Any]], float, Dict[str, Any]]:
        """
        Matches a user query against the 200 questions in `ai_question_bank`.
        Returns: (best_match_dict, similarity_score, extracted_entities)
        """
        questions = self.load_question_bank(conn)
        entities = self.extract_entities(query, conn)

        # 1. Exact Question Code check (e.g. user asks "What is Q025?" or "Q145")
        code_match = re.search(r"\b(Q\d{3})\b", query, re.IGNORECASE)
        if code_match:
            target_code = code_match.group(1).upper()
            for q in questions:
                if q["question_code"] == target_code:
                    return q, 1.0, entities

        # 2. Token overlap similarity with domain term weighting
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return None, 0.0, entities

        best_score = 0.0
        best_match = None

        KEYWORD_WEIGHTS = {
            "dropout": 2.5, "absenteeism": 2.5, "attendance": 2.0, "marks": 2.0,
            "rte": 3.0, "scholarship": 2.5, "ssp": 3.0, "nmms": 3.0, "transfer": 2.5,
            "tc": 3.0, "uniform": 2.0, "textbook": 2.0, "mid-day": 2.5, "poshan": 2.5,
            "remedial": 2.0, "vacancies": 2.0, "capacity": 2.0, "overcrowding": 2.5,
            "vacancy": 2.0, "bridge": 2.5, "complaint": 2.0, "inspection": 2.0,
            "kannada": 2.0, "english": 2.0, "laboratory": 2.0, "computer": 2.0,
            "hostel": 2.0, "disabilities": 2.5, "disabled": 2.5, "special": 2.0,
            "pre-matric": 3.0, "post-matric": 3.0, "timetable": 2.0, "olympiad": 2.5
        }

        for q in questions:
            q_tokens = q["tokens"]
            common = query_tokens.intersection(q_tokens)
            if not common:
                continue

            # Weighted intersection
            weighted_common = sum(KEYWORD_WEIGHTS.get(w, 1.0) for w in common)
            weighted_union = sum(KEYWORD_WEIGHTS.get(w, 1.0) for w in query_tokens.union(q_tokens))
            jaccard = weighted_common / weighted_union if weighted_union > 0 else 0.0

            # Boost if key entities match
            if entities.get("district") and entities["district"].lower() in q["question_text"].lower():
                jaccard += 0.15
            if entities.get("standard") and entities["standard"] in q["question_text"]:
                jaccard += 0.15

            if jaccard > best_score:
                best_score = jaccard
                best_match = q

        return best_match, min(1.0, best_score), entities
