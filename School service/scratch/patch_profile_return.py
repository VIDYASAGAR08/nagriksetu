path = r'C:\Users\callm\nagriksetu\backend\main.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = """        return {
            "personal_info": {
                "student_id": student["student_id"],
                "permanent_student_id": student["permanent_student_id"],
                "admission_number": student["student_id"],
                "student_name": student["student_name"],
                "date_of_birth": student.get("date_of_birth") or "2013-06-15",
                "gender": student.get("gender") or "Not specified",
                "age": student.get("age"),
                "first_language": student.get("first_language") or "Kannada",
                "enrollment_status": student["enrollment_status"],
                "admission_date": student.get("admission_date") or "2024-06-01"
            },
            "academic_info": {
                "school_id": student["school_id"],
                "school_name": student["school_name"],
                "school_type": student["school_type"],
                "category": student["category"],
                "standard": student["standard"],
                "section": student["section"],
                "academic_year": enrollment.get("academic_year") if enrollment else "2026-2027",
                "stream": enrollment.get("stream") if enrollment else None,
                "subject_combination": enrollment.get("subject_combination") if enrollment else None
            },
            "parent_info": guardians,
            "attendance": {
                "has_records": attendance_summary is not None,
                "summary": attendance_summary,
                "records": attendance_records
            },
            "examinations": {
                "has_records": len(exam_results) > 0,
                "results": exam_results
            },
            "sgpa_cgpa": sgpa_cgpa,
            "documents": documents
        }"""

replacement = """        pers_data = {
            "student_id": student["student_id"],
            "permanent_student_id": student["permanent_student_id"],
            "admission_number": student["student_id"],
            "student_name": student["student_name"],
            "date_of_birth": student.get("date_of_birth") or "2013-06-15",
            "gender": student.get("gender") or "Not specified",
            "age": student.get("age"),
            "first_language": student.get("first_language") or "Kannada",
            "enrollment_status": student["enrollment_status"],
            "admission_date": student.get("admission_date") or "2024-06-01"
        }
        acad_data = {
            "school_id": student["school_id"],
            "school_name": student["school_name"],
            "school_type": student["school_type"],
            "category": student["category"],
            "standard": student["standard"],
            "section": student["section"],
            "academic_year": enrollment.get("academic_year") if enrollment else "2026-2027",
            "stream": enrollment.get("stream") if enrollment else None,
            "subject_combination": enrollment.get("subject_combination") if enrollment else None
        }
        return {
            "personal_info": pers_data,
            "personal": pers_data,
            "academic_info": acad_data,
            "academic": acad_data,
            "parent_info": guardians,
            "parent_guardian": guardians[0] if guardians else None,
            "attendance": {
                "has_records": attendance_summary is not None,
                "summary": attendance_summary,
                "records": attendance_records
            },
            "attendance_records": attendance_records,
            "attendance_summary": attendance_summary,
            "examinations": {
                "has_records": len(exam_results) > 0,
                "results": exam_results
            },
            "examination_results": exam_results,
            "sgpa_cgpa": sgpa_cgpa,
            "documents": documents
        }"""

if target in text:
    text = text.replace(target, replacement)
    print("Patched profile return dict!")
elif target.replace('\n', '\r\n') in text:
    text = text.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'))
    print("Patched profile return dict CRLF!")
else:
    print("Profile return target not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
