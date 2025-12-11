from __future__ import annotations
from datetime import datetime, date as date_type
from enum import Enum
from typing import Optional, List, Dict
from bson import ObjectId

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class StudentStatus(str, Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    DROPPED_OUT = "Dropped Out"
    GRADUATED = "Graduated"

class Student:
    """
    Student Domain Entity.
    Separated from IAM (User). This represents the 'Academic Profile'.
    """
    def __init__(
        self,
        user_id: ObjectId,
        student_id_code: str,
        first_name_kh: str,
        last_name_kh: str,
        first_name_en: str,
        last_name_en: str,
        gender: Gender | str,
        dob: date_type,
        current_grade_level: int,
        id: Optional[ObjectId] = None,
        photo_url: Optional[str] = None,
        phone_number: Optional[str] = None,
        address: Optional[Dict] = None,
        guardians: Optional[List[Dict]] = None,
        status: StudentStatus | str = StudentStatus.ACTIVE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or ObjectId()
        self.user_id = user_id
        self.student_id_code = student_id_code
        self.first_name_kh = first_name_kh
        self.last_name_kh = last_name_kh
        self.first_name_en = first_name_en
        self.last_name_en = last_name_en
        self.gender = Gender(gender) if isinstance(gender, str) else gender
        self.dob = dob
        self.current_grade_level = current_grade_level
        self.photo_url = photo_url
        self.phone_number = phone_number
        self.address = address or {}
        self.guardians = guardians or []
        self.status = StudentStatus(status) if isinstance(status, str) else status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_profile(self, first_name_en: str, last_name_en: str):
        self.first_name_en = first_name_en
        self.last_name_en = last_name_en
        self.updated_at = datetime.utcnow()

    def promote_grade(self):
        if self.current_grade_level < 12:
            self.current_grade_level += 1
            self.updated_at = datetime.utcnow()