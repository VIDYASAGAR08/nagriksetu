"""
NagrikSetu AI Engine - Central Universal AI Assistant Orchestrator
Coordinates question matching, context tracking, RBAC validation, DB queries,
official knowledge retrieval, and LLM provider synthesis.
"""

import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

from .question_matcher import QuestionMatcher
from .knowledge_base import search_official_knowledge
from .db_tools import DatabaseTools
from .rbac import AccessGuard
from .conversation import conversation_manager
from .providers import get_ai_provider

OUT_OF_SCOPE_KEYWORDS = [
    "cricket", "football", "movie", "cinema", "actor", "actress",
    "cryptocurrency", "bitcoin", "stock market", "weather forecast",
    "recipe", "cooking", "astrology", "horoscope", "video game"
]

class UniversalAIAssistant:
    def __init__(self):
        self.matcher = QuestionMatcher()

    def process_message(
        self,
        conn: sqlite3.Connection,
        user_message: str,
        user: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        session = conversation_manager.get_or_create(session_id)
        text = user_message.strip()
        text_lower = text.lower()
        role = AccessGuard.get_user_role(user)

        # 1. Out-of-Scope Detection
        if any(w in text_lower for w in OUT_OF_SCOPE_KEYWORDS):
            resp = (
                "ℹ️ **Out of Scope Inquiry**\n\n"
                "NagrikSetu AI Assistance is dedicated to Karnataka School Education Services, "
                "school discovery, admissions, scholarships, academic guidance, and school administration. "
                "I am unable to answer questions unrelated to school education.\n\n"
                "How can I assist you with schools, admissions, student records, or government schemes today?"
            )
            session.add_turn(user_message, resp)
            return {
                "response": resp,
                "session_id": session.session_id,
                "intent": "Out of Scope",
                "category": "General",
                "matched_question": None,
                "grounded_sources": ["System Domain Filter"],
                "suggested_actions": ["Search Government Schools", "Check RTE Guidelines", "Explore Scholarships"],
                "role_context": role,
                "provider_info": get_ai_provider().get_info()
            }

        # 2. Statutory Policy Guardrail: Automated Decision Prohibition
        if re.search(r"\b(approve|reject|enroll|decide)\b.*\b(admission|application|student)\b", text_lower) or any(k in text_lower for k in ["approve this application", "reject application", "confirm admission decision"]):
            resp = (
                "🛡️ **Statutory Compliance Policy**\n\n"
                "Under Karnataka Public Education Governance regulations, AI assistants are strictly prohibited "
                "from executing or overturning official admission decisions. Admission approvals, rejections, "
                "and seat allotments must be formally authorized by a designated human institutional admissions officer."
            )
            session.add_turn(user_message, resp)
            return {
                "response": resp,
                "session_id": session.session_id,
                "intent": "Automated Decision Prohibition",
                "category": "School Administration",
                "matched_question": None,
                "grounded_sources": ["Policy: Automated Decision-Making Prohibition (Section 12.4)"],
                "suggested_actions": ["Review in Staff Admission Desk"],
                "role_context": role,
                "provider_info": get_ai_provider().get_info()
            }

        # 3. Match against the 200-question bank
        best_match, match_score, entities = self.matcher.match_question(text, conn)

        # Multi-turn context resolution: borrow context if follow-up question
        is_follow_up = False
        if not entities["district"] and session.context_entities["last_district"]:
            if any(w in text_lower for w in ["these", "those", "there", "them", "which of", "what about", "and in"]):
                entities["district"] = session.context_entities["last_district"]
                is_follow_up = True
        if not entities["institution_ids"] and session.context_entities["last_school_ids"]:
            if any(w in text_lower for w in ["this school", "these schools", "their", "them", "admission process", "fees"]):
                entities["institution_ids"] = session.context_entities["last_school_ids"]
                is_follow_up = True

        session.update_context(entities, topic=best_match["category"] if best_match else None)

        sources: List[str] = []
        actions: List[str] = []
        matched_info = None
        if best_match:
            matched_info = {
                "code": best_match["question_code"],
                "text": best_match["question_text"],
                "category": best_match["category"],
                "similarity": round(match_score, 2)
            }

        # 4. PRIVACY BOUNDARIES & RBAC: Personal Student / Parent Queries
        is_personal_query = (
            any(k in text_lower for k in [
                "my attendance", "check my attendance", "my child's attendance", "child attendance",
                "my marks", "my result", "my report card", "my child's marks", "my child's result",
                "my application", "application status", "track my application", "my admission", "my permanent id"
            ]) or 
            ("my child" in text_lower and any(w in text_lower for w in ["marks", "attendance", "result", "report", "grade", "progress", "linking", "fee status"]))
        )

        if is_personal_query:
            if role == "public":
                resp = (
                    "🔒 **Authentication Required for Private Records**\n\n"
                    "Student academic results, attendance tracking, and Stage 1/Stage 2 admission applications "
                    "are protected under NagrikSetu privacy safeguards.\n\n"
                    "Please sign in to your verified **Parent** or **Student** account to query private records."
                )
                session.add_turn(user_message, resp)
                return {
                    "response": resp,
                    "session_id": session.session_id,
                    "intent": "Private Record Access Request",
                    "category": "Parent and Child Support",
                    "matched_question": matched_info,
                    "grounded_sources": ["Privacy Guard: Public Data Isolation"],
                    "suggested_actions": ["Sign In to Account", "Browse Public Schools"],
                    "role_context": "public",
                    "provider_info": get_ai_provider().get_info()
                }

            # Parent User Queries
            if role == "parent":
                if any(k in text_lower for k in ["application", "admission status", "stage 1", "stage 2"]):
                    apps = DatabaseTools.get_parent_applications(conn, user["user_id"])
                    if not apps:
                        resp = "You currently have no admission applications submitted under this verified parent account."
                        actions = ["Submit Stage 1 Application", "Browse Schools"]
                    else:
                        lines = ["📋 **Your Real-Time Admission Application Statuses**:"]
                        for a in apps:
                            lines.append(
                                f"• **Application ID**: `{a['application_id']}`\n"
                                f"  - **Applicant**: {a['applicant_name']}\n"
                                f"  - **Institution**: {a['school_name']} ({a['institution_id']})\n"
                                f"  - **Status**: **{a['status'].replace('_', ' ').title()}** (Standard {a['requested_standard']})"
                            )
                            sources.append(f"admission_applications: {a['application_id']}")
                        resp = "\n\n".join(lines)
                        actions = ["Complete Stage 2 Dossier", "Track Application Updates"]

                    session.add_turn(user_message, resp)
                    return {
                        "response": resp,
                        "session_id": session.session_id,
                        "intent": "Parent Admission Applications",
                        "category": "Admissions, Transfers and Records",
                        "matched_question": matched_info,
                        "grounded_sources": sources or ["admission_applications table"],
                        "suggested_actions": actions,
                        "role_context": "parent",
                        "provider_info": get_ai_provider().get_info()
                    }

                # Parent querying linked children
                if any(k in text_lower for k in ["child", "children", "attendance", "marks", "result"]):
                    children = DatabaseTools.get_parent_children(conn, user["user_id"])
                    if not children:
                        resp = (
                            "ℹ️ **No Verified Linked Children**\n\n"
                            "You do not currently have any officially verified children linked to your parent portal. "
                            "Please submit a Student Linking Request in your Parent Dashboard."
                        )
                        actions = ["Submit Student Linking Request"]
                    else:
                        lines = ["👨‍👩‍👧 **Your Verified Linked Children**:\n"]
                        for c in children:
                            pid = c["permanent_student_id"]
                            lines.append(
                                f"• **{c['student_name']}** (`{pid}`)\n"
                                f"  - **School**: {c['school_name']} ({c['school_id']})\n"
                                f"  - **Class**: Standard {c['standard']}-{c['section']} (Language: {c['first_language']})\n"
                                f"  - **Enrollment**: {c['enrollment_status'].title()}"
                            )
                            sources.append(f"students: {pid}")

                            if "attendance" in text_lower:
                                att = DatabaseTools.get_student_attendance(conn, pid)
                                lines.append(
                                    f"  - **Attendance**: {att['attendance_percentage']}% "
                                    f"({att['present_days']} present out of {att['total_recorded_days']} recorded days)"
                                )
                                sources.append(f"student_attendance: {pid}")

                        resp = "\n".join(lines)
                        actions = ["View Child Academic Performance", "Submit Update Request"]

                    session.add_turn(user_message, resp)
                    return {
                        "response": resp,
                        "session_id": session.session_id,
                        "intent": "Parent Child Records",
                        "category": "Parent and Child Support",
                        "matched_question": matched_info,
                        "grounded_sources": sources,
                        "suggested_actions": actions,
                        "role_context": "parent",
                        "provider_info": get_ai_provider().get_info()
                    }

            # Student User Queries
            if role == "student":
                is_auth, reason, perm_id = AccessGuard.verify_student_self_access(conn, user)
                if not is_auth:
                    resp = f"🔒 {reason}"
                    session.add_turn(user_message, resp)
                    return {
                        "response": resp,
                        "session_id": session.session_id,
                        "intent": "Student Self Access",
                        "category": "Student Academic Guidance and Learning",
                        "matched_question": matched_info,
                        "grounded_sources": ["Privacy Guard: Student Isolation"],
                        "suggested_actions": ["View My Dashboard"],
                        "role_context": "student",
                        "provider_info": get_ai_provider().get_info()
                    }

                if "attendance" in text_lower:
                    att = DatabaseTools.get_student_attendance(conn, perm_id or "STU-DEMO")
                    resp = (
                        f"📊 **Your Official Attendance Record** (`{att['permanent_student_id']}`):\n\n"
                        f"• **Student Name**: {att['student_name']}\n"
                        f"• **Institution**: {att['school_name']} ({att['standard']})\n"
                        f"• **Total Recorded Sessions**: {att['total_recorded_days']} days\n"
                        f"• **Present**: {att['present_days']} days\n"
                        f"• **Absent**: {att['absent_days']} days\n"
                        f"• **Cumulative Attendance Rate**: **{att['attendance_percentage']}%**"
                    )
                    session.add_turn(user_message, resp)
                    return {
                        "response": resp,
                        "session_id": session.session_id,
                        "intent": "Student Attendance Summary",
                        "category": "Student Academic Guidance and Learning",
                        "matched_question": matched_info,
                        "grounded_sources": [f"student_attendance: {perm_id}"],
                        "suggested_actions": ["View Subject Breakdown", "Check Timetable"],
                        "role_context": "student",
                        "provider_info": get_ai_provider().get_info()
                    }

        # 5. STAFF / ADMIN QUERIES
        if role in ["school_staff", "school_admin"] and any(k in text_lower for k in ["admission desk", "pending application", "desk status", "section capacity", "strength"]):
            sid = user.get("school_id")
            if sid:
                if any(k in text_lower for k in ["capacity", "strength", "seat"]):
                    secs = DatabaseTools.get_section_strengths(conn, sid)
                    lines = [f"💺 **Section Capacities & Vacancies for {sid}**:"]
                    for s in secs:
                        rem = max(0, s["capacity"] - s["current_strength"])
                        stat = "❌ Full" if rem == 0 else f"✓ {rem} Open"
                        lines.append(f"• **Class {s['term_or_year']} {s['section_name']}**: Enrolled {s['current_strength']}/{s['capacity']} ({stat})")
                    resp = "\n".join(lines)
                    sources.append(f"program_sections for {sid}")
                    actions = ["Manage Sections", "Confirm Admissions"]
                else:
                    desk = DatabaseTools.get_school_admin_desk(conn, sid)
                    resp = (
                        f"📊 **Admission Desk Operational Summary for Institution `{sid}`**:\n\n"
                        f"• **Total Applications**: {desk.get('total_apps', 0)}\n"
                        f"• **Pending Stage 1 Review**: {desk.get('pending_review', 0)}\n"
                        f"• **Under Active Review**: {desk.get('in_review', 0)}\n"
                        f"• **Stage 1 Approved (Awaiting Stage 2 Dossier)**: {desk.get('stage1_approved', 0)}\n"
                        f"• **Stage 2 Dossier & Documents Submitted**: {desk.get('stage2_submitted', 0)}\n"
                        f"• **Officially Enrolled Students**: {desk.get('enrolled', 0)}"
                    )
                    sources.append(f"admission_applications for {sid}")
                    actions = ["Open Staff Admission Desk", "Review Stage 1 Submissions"]

                session.add_turn(user_message, resp)
                return {
                    "response": resp,
                    "session_id": session.session_id,
                    "intent": "Staff Desk Summary",
                    "category": "School Administration",
                    "matched_question": matched_info,
                    "grounded_sources": sources,
                    "suggested_actions": actions,
                    "role_context": role,
                    "provider_info": get_ai_provider().get_info()
                }

        # 6. OFFICIAL GOVERNMENT KNOWLEDGE BASE (RTE, Scholarships, Schemes, TC, Bridge)
        official_kb = search_official_knowledge(text)
        if official_kb and not any(k in text_lower for k in ["how many schools in", "list schools in", "compare"]):
            lines = [f"🏛️ **{official_kb['title']}**\n"]
            lines.append(f"• **Governing Authority**: {official_kb['authority']}")
            if "governing_law" in official_kb:
                lines.append(f"• **Statutory Framework**: {official_kb['governing_law']}")
            if "target_students" in official_kb:
                lines.append(f"• **Target Group**: {official_kb['target_students']}")

            lines.append("\n**Official Statutory Facts & Guidelines**:")
            for fact in official_kb["key_facts"]:
                lines.append(f"• {fact}")

            if "important_note" in official_kb:
                lines.append(f"\n⚠️ *Important Notice*: {official_kb['important_note']}")
            if "application_mode" in official_kb:
                lines.append(f"\n🔗 **Application Mode**: {official_kb['application_mode']}")

            resp = "\n".join(lines)
            sources.append(f"Official Knowledge Base: {official_kb['title']}")
            actions = ["Find Neighborhood Schools", "Check Document Checklist", "Download Official Guidelines"]

            session.add_turn(user_message, resp)
            return {
                "response": resp,
                "session_id": session.session_id,
                "intent": "Official Scheme Knowledge",
                "category": best_match["category"] if best_match else "Government Schemes and Student Welfare",
                "matched_question": matched_info,
                "grounded_sources": sources,
                "suggested_actions": actions,
                "role_context": role,
                "provider_info": get_ai_provider().get_info()
            }

        # 7. INSTITUTION COMPARISON QUERIES
        inst_ids = entities.get("institution_ids", [])
        if "compare" in text_lower or len(inst_ids) >= 2:
            if len(inst_ids) >= 2:
                comp = DatabaseTools.compare_institutions(conn, inst_ids[0], inst_ids[1])
                if comp:
                    s1, s2 = comp
                    v1 = max(0, s1["total_capacity"] - s1["total_enrolled"])
                    v2 = max(0, s2["total_capacity"] - s2["total_enrolled"])
                    resp = (
                        f"⚖️ **Institutional Comparison: {s1['school_name']} vs. {s2['school_name']}**\n\n"
                        f"| Parameter | {s1['school_name']} (`{s1['school_id']}`) | {s2['school_name']} (`{s2['school_id']}`) |\n"
                        f"|---|---|---|\n"
                        f"| **Type** | {s1['school_type']} | {s2['school_type']} |\n"
                        f"| **District** | {s1['district']}, {s1['state']} | {s2['district']}, {s2['state']} |\n"
                        f"| **Board / Affiliation** | {s1['affiliation'] or 'State Board'} | {s2['affiliation'] or 'State Board'} |\n"
                        f"| **Sanctioned Capacity** | {s1['total_capacity']:,} seats | {s2['total_capacity']:,} seats |\n"
                        f"| **Enrolled Strength** | {s1['total_enrolled']:,} students | {s2['total_enrolled']:,} students |\n"
                        f"| **Open Vacancies** | {v1:,} seats | {v2:,} seats |\n"
                    )
                    sources = [f"schools: {s1['school_id']}", f"schools: {s2['school_id']}"]
                    actions = [f"View {s1['school_id']}", f"View {s2['school_id']}"]
                    session.add_turn(user_message, resp)
                    return {
                        "response": resp,
                        "session_id": session.session_id,
                        "intent": "Institution Comparison",
                        "category": "School Discovery and Admissions",
                        "matched_question": matched_info,
                        "grounded_sources": sources,
                        "suggested_actions": actions,
                        "role_context": role,
                        "provider_info": get_ai_provider().get_info()
                    }

        # 8. SPECIFIC INSTITUTION PROFILE
        if inst_ids:
            school = DatabaseTools.get_school_profile(conn, inst_ids[0])
            if school:
                progs_str = ", ".join([p["program_name"] for p in school.get("programs", [])]) or "Standards 1 to 10 Curriculum"
                vacancies = max(0, school["total_capacity"] - school["total_enrolled"])
                resp = (
                    f"🏫 **{school['school_name']} (`{school['school_id']}`)**\n\n"
                    f"• **Institution Type**: {school['school_type'].replace('_', ' ').title()}\n"
                    f"• **District & State**: {school['district']}, {school['state']}\n"
                    f"• **Address**: {school.get('address') or 'N/A'}\n"
                    f"• **Affiliation / Board**: {school.get('affiliation') or 'Karnataka State Board'}\n"
                    f"• **Academic Offerings**: {progs_str}\n"
                    f"• **Total Capacity**: {school['total_capacity']:,} seats ({vacancies:,} vacant seats)\n"
                    f"• **Public Discovery Route**: Accessible at `/schools/{school['school_id']}`"
                )
                sources.append(f"schools: {school['school_id']}")
                actions = [f"View Profile for {school['school_id']}", f"Apply at {school['school_id']}"]
                session.add_turn(user_message, resp)
                return {
                    "response": resp,
                    "session_id": session.session_id,
                    "intent": "School Profile",
                    "category": "School Discovery and Admissions",
                    "matched_question": matched_info,
                    "grounded_sources": sources,
                    "suggested_actions": actions,
                    "role_context": role,
                    "provider_info": get_ai_provider().get_info()
                }

        # 9. GENERAL SEAT VACANCIES
        if any(k in text_lower for k in ["vacanc", "seat", "capacity", "available seats"]):
            seats = DatabaseTools.get_seat_vacancies_overview(conn)
            resp = (
                f"💺 **Statewide Academic Seat Capacity & Vacancy Overview**:\n\n"
                f"• **Total Sanctioned Seats**: {seats['total_capacity']:,} seats across {seats['total_sections']} sections\n"
                f"• **Currently Enrolled**: {seats['total_enrolled']:,} students\n"
                f"• **Available Vacant Seats**: **{seats['open_vacancies']:,} open seats** statewide\n\n"
                f"You can explore live section-by-section availability under any institution profile."
            )
            sources.append("program_sections (841 sections)")
            actions = ["Browse All Schools", "Filter by District"]
            session.add_turn(user_message, resp)
            return {
                "response": resp,
                "session_id": session.session_id,
                "intent": "Statewide Seat Overview",
                "category": "School Discovery and Admissions",
                "matched_question": matched_info,
                "grounded_sources": sources,
                "suggested_actions": actions,
                "role_context": role,
                "provider_info": get_ai_provider().get_info()
            }

        # 10. SCHOOL DIRECTORY SEARCH (by district, type, standard, query)
        dist = entities.get("district")
        stype = "government" if ("government" in text_lower or "govt" in text_lower) else ("private" if "private" in text_lower else None)
        schools = DatabaseTools.search_schools(conn, district=dist, school_type=stype, limit=5)

        if schools:
            lines = [f"🔍 Found {len(schools)} verified educational institutions{' in ' + dist if dist else ''}:"]
            for s in schools:
                board = s["affiliation"] or s["recognition"] or "Karnataka State Board"
                facs_raw = s.get("facilities")
                if isinstance(facs_raw, dict):
                    facs_list = facs_raw.get("campus_facilities", [])
                elif isinstance(facs_raw, list):
                    facs_list = facs_raw
                else:
                    facs_list = []
                facs = ", ".join(facs_list[:3]) or "Library, Laboratories, Playground"
                lines.append(
                    f"• **{s['school_name']}** (`{s['school_id']}`)\n"
                    f"  - **Type**: {s['school_type'].replace('_', ' ').title()}\n"
                    f"  - **District**: {s['district']} • **Affiliation**: {board}\n"
                    f"  - **Facilities**: {facs}"
                )
                sources.append(f"schools: {s['school_id']}")
            resp = "\n\n".join(lines)
            actions = ["View School Details", "Check Live Seat Availability"]
            session.add_turn(user_message, resp)
            return {
                "response": resp,
                "session_id": session.session_id,
                "intent": "School Discovery",
                "category": "School Discovery and Admissions",
                "matched_question": matched_info,
                "grounded_sources": sources,
                "suggested_actions": actions,
                "role_context": role,
                "provider_info": get_ai_provider().get_info()
            }

        # 11. GENERAL EDUCATIONAL GUIDANCE / DEFAULT
        fallback_cat = best_match["category"] if best_match else "General"
        resp = (
            "Namaskara! Welcome to **NagrikSetu AI Assistance** for Karnataka School Services.\n\n"
            "I can assist you with:\n"
            "• **School Discovery**: Search 30 verified institutions, facilities, and live vacancies.\n"
            "• **RTE & Schemes**: Learn about 25% RTE reserved quota, pre-matric/post-matric scholarships, and free uniforms/textbooks.\n"
            "• **Student Services**: Attendance summaries, academic guidance, and examination schedules.\n"
            "• **Parent Portal**: Track Stage 1/Stage 2 admission applications and monitor linked children.\n"
            "• **Institutional Desk**: Operational summaries and section capacity ledgers.\n\n"
            "Please ask any question, or select an example topic to get started!"
        )
        sources.append("NagrikSetu Education Knowledge Base")
        actions = ["Find Government Schools", "What are RTE guidelines?", "Check Scholarship Eligibility"]
        session.add_turn(user_message, resp)
        return {
            "response": resp,
            "session_id": session.session_id,
            "intent": "General Welcome & Guidance",
            "category": fallback_cat,
            "matched_question": matched_info,
            "grounded_sources": sources,
            "suggested_actions": actions,
            "role_context": role,
            "provider_info": get_ai_provider().get_info()
        }

assistant_orchestrator = UniversalAIAssistant()
