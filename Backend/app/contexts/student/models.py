from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List
from bson import ObjectId
from app.contexts.shared.enum.roles import UserRole


# -------------------------
# Payload
# -------------------------
@dataclass
class StudentUpdatePayload:
    student_id: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    grade_level: Optional[int] = None
    classes: Optional[List[ObjectId]] = field(default_factory=list)
    enrollment_date: Optional[date] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    parent_number: Optional[str] = None

    def to_dict(self, safe: bool = False):
        data = {**self.__dict__}
        if safe:            data["classes"] = [str(c) for c in self.classes]
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
    nickname: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    grade_level: Optional[int] = None
    classes: List[ObjectId] = field(default_factory=list)
    enrollment_date: Optional[date] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    parent_number: Optional[str] = None

    def to_dict(self, safe: bool = False):
        data = {**self.__dict__}
        if safe:
            data["classes"] = [str(c) for c in self.classes]
        return data

    def to_persistence_dict(self):
        return {**self.__dict__}


class Student:
    def __init__(self, user_id: str, student_info: StudentInfo):
        self.user_id = user_id
        self.student_info = student_info
        self.role = UserRole.STUDENT

    # Domain logic
    def add_class(self, class_id: str):
        if class_id not in self.student_info.classes:
            self.student_info.classes.append(class_id)

    def remove_class(self, class_id: str):
        if class_id in self.student_info.classes:
            self.student_info.classes.remove(class_id)

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
    def create_from_payload(cls, user_id: str, payload: StudentUpdatePayload) -> Student:
        student_info = StudentInfo(
            user_id=user_id,
            student_id=payload.student_id,
            full_name=payload.full_name
        )
        return Student(user_id=user_id, student_info=student_info)


# -------------------------
# Mapper
# -------------------------
class StudentMapper:
    @classmethod
    def to_domain(cls, data: dict) -> Student:
        student_info_data = data.get("student_info", {}).copy()
        student_info = StudentInfo(**student_info_data)
        return Student(
            user_id=str(data.get("_id") or data.get("user_id")),
            student_info=student_info
        )

    @staticmethod
    def to_persistence_dict(student: Student) -> dict:
        return {
            "_id": ObjectId(student.user_id) if ObjectId.is_valid(student.user_id) else student.user_id,
            "user_id": student.user_id,
            "role": student.role.value,
            "student_info": student.student_info.to_dict(safe=False)
        }

    @staticmethod
    def to_safe_dict(student: Student) -> dict:
        return {
            "user_id": str(student.user_id),
            "role": student.role.value,
            "student_info": student.student_info.to_dict(safe=True)
        }