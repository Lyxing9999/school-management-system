from __future__ import annotations
from dataclasses import dataclass, field, fields
from datetime import datetime, date
from typing import Optional, List
from bson import ObjectId
from app.contexts.shared.enum.roles import UserRole
from app.contexts.student.data_transfer.responses import StudentInfoBaseDataDTO

# -------------------------
# Payload
# -------------------------
@dataclass
class StudentUpdatePayload:
    student_id: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    grade_level: Optional[int] = None
    classes: Optional[List[str]] = field(default_factory=list)
    enrollment_date: Optional[date] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    parent_number: Optional[str] = None

    def to_dict(self, safe: bool = False):
        data = {**self.__dict__}
        if safe:
            data["classes"] = [str(c) for c in self.classes]
        return data

# -------------------------
# Domain Model
# -------------------------
@dataclass
class StudentInfo:
    student_id: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    grade_level: Optional[int] = None
    classes: List[str] = field(default_factory=list)
    enrollment_date: Optional[datetime] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    parent_number: Optional[str] = None

    def to_dict(self, safe: bool = False):
        data = {**self.__dict__}
        if safe:
            data["classes"] = [str(c) for c in self.classes]
        return data

# -------------------------
# Aggregate Root
# -------------------------
class Student:
    def __init__(self, user_id: ObjectId, student_info: StudentInfo, _id: Optional[ObjectId] = None):
        self.id = _id
        self.user_id = user_id
        self.student_info = student_info
        self.role = UserRole.STUDENT

    def update_info(self, payload: StudentUpdatePayload):
        allowed_fields = [f.name for f in fields(StudentInfo)]
        for key, value in payload.__dict__.items():
            if value is not None and key in allowed_fields:
                setattr(self.student_info, key, value)

# -------------------------
# Factory
# -------------------------
class StudentFactory:
    @classmethod
    def create_from_payload(cls, user_id: ObjectId, payload: StudentUpdatePayload) -> Student:
        student_info = StudentInfo(
            student_id=payload.student_id,
            full_name=payload.full_name,
            first_name=payload.first_name,
            last_name=payload.last_name,
            birth_date=datetime.combine(payload.birth_date, datetime.min.time()) if payload.birth_date else None,
            gender=payload.gender,
            grade_level=payload.grade_level,
            classes=payload.classes or [],
            enrollment_date=datetime.combine(payload.enrollment_date, datetime.min.time()) if payload.enrollment_date else None,
            address=payload.address,
            photo_url=payload.photo_url,
            parent_number=payload.parent_number,
        )
        return Student(user_id=user_id, student_info=student_info)

# -------------------------
# Mapper
# -------------------------
class StudentMapper:
    @classmethod
    def to_domain(cls, data: dict) -> Student:
        student_info_data = data.get("student_info", {}).copy()
        if "student_info" in student_info_data:
            student_info_data = student_info_data["student_info"]
        for key in ["_id", "user_id", "role"]:
            student_info_data.pop(key, None)
        for key in ["birth_date", "enrollment_date"]:
            if key in student_info_data:
                if isinstance(student_info_data[key], str):
                    student_info_data[key] = datetime.strptime(student_info_data[key], "%Y-%m-%d")
                elif isinstance(student_info_data[key], date) and not isinstance(student_info_data[key], datetime):
                    student_info_data[key] = datetime.combine(student_info_data[key], datetime.min.time())
        student_info = StudentInfo(**student_info_data)

        # Convert user_id and _id
        user_id = data.get("user_id")
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        _id = data.get("_id")
        if isinstance(_id, str):
            _id = ObjectId(_id)

        return Student(user_id=user_id, student_info=student_info, _id=_id)

    @staticmethod
    def to_persistence_dict(student: Student) -> dict:
        info_dict = student.student_info.to_dict(safe=False).copy()
        # Ensure all dates are datetime
        for key in ["birth_date", "enrollment_date"]:
            if info_dict.get(key) and isinstance(info_dict[key], date) and not isinstance(info_dict[key], datetime):
                info_dict[key] = datetime.combine(info_dict[key], datetime.min.time())

        return {
            "_id": student.id or ObjectId(),
            "user_id": student.user_id,
            "role": student.role.value,
            "student_info": info_dict
        }

    @staticmethod
    def to_safe_dict(student: Student) -> dict:
        return {
            "user_id": str(student.user_id),
            "role": student.role.value,
            "student_info": student.student_info.to_dict(safe=True)
        }

    @staticmethod
    def to_dto(student: Student) -> StudentInfoBaseDataDTO:
        return StudentInfoBaseDataDTO(
            id=str(student.id) if student.id else None,
            student_id=student.student_info.student_id,
            full_name=student.student_info.full_name,
            first_name=student.student_info.first_name,
            last_name=student.student_info.last_name,
            birth_date=student.student_info.birth_date,
            gender=student.student_info.gender,
            grade_level=student.student_info.grade_level,
            classes=student.student_info.classes,
            enrollment_date=student.student_info.enrollment_date,
            address=student.student_info.address,
            photo_url=student.student_info.photo_url,
            parent_number=student.student_info.parent_number
        )