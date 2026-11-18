# Check syntax of proposed academic module additions
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class AttendanceEntryItem(BaseModel):
    permanent_student_id: str
    status: Literal["present", "absent", "leave"]
    remarks: Optional[str] = None

class BatchAttendanceRecordPayload(BaseModel):
    institution_id: str
    attendance_date: str = Field(min_length=10, max_length=10)
    subject_name: Optional[str] = None
    records: List[AttendanceEntryItem]

class ExaminationCreatePayload(BaseModel):
    institution_id: str
    academic_year: str = "2026-2027"
    exam_name: str = Field(min_length=2, max_length=100)
    standard_or_level: str = Field(min_length=1, max_length=50)
    start_date: str = Field(min_length=10, max_length=10)
    end_date: Optional[str] = None
    status: Literal["scheduled", "ongoing", "completed", "cancelled"] = "scheduled"
    description: Optional[str] = None

class ResultEntryItem(BaseModel):
    permanent_student_id: str
    marks_obtained: float = Field(ge=0)
    reason_for_change: Optional[str] = None

class BatchResultRecordPayload(BaseModel):
    institution_id: str
    academic_year: str = "2026-2027"
    exam_name: str = Field(min_length=2, max_length=100)
    subject_name: str = Field(min_length=2, max_length=100)
    maximum_marks: float = Field(gt=0)
    exam_date: Optional[str] = None
    exam_id: Optional[str] = None
    records: List[ResultEntryItem]

class AnnouncementCreatePayload(BaseModel):
    institution_id: str
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=5, max_length=5000)
    target_audience: Literal["all", "students", "parents", "staff"] = "all"

print("Pydantic models valid!")
