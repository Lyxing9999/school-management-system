from __future__ import annotations

from datetime import datetime, date as date_type
from enum import Enum
from typing import Optional, List, Dict, Any
from bson import ObjectId

# Import Exceptions របស់បង
from app.contexts.student.errors.student_exceptions import (
    StudentDobTypeInvalidException,
    StudentDobInFutureException,
    StudentAgeOutOfRangeException,
    StudentDobStringFormatInvalidException,
    StudentCannotJoinClassWhenNotActiveException
)

# --- Enums ---
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class StudentStatus(str, Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    DROPPED_OUT = "Dropped Out"
    GRADUATED = "Graduated"
    ARCHIVED = "Archived" 

# --- Domain Entity ---
class Student:
    """
    Student Domain Entity.
    The core business logic for a Student profile.
    """

    MIN_AGE_YEARS = 5
    MAX_AGE_YEARS = 35

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
        current_class_id: Optional[ObjectId] = None,  
    
        id: Optional[ObjectId] = None,
        photo_url: Optional[str] = None,
        phone_number: Optional[str] = None,
        address: Optional[Dict] = None,
        guardians: Optional[List[Dict]] = None,
        status: StudentStatus | str = StudentStatus.ACTIVE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ):
        self.id = id or ObjectId()
        self.user_id = user_id
        self.student_id_code = student_id_code
        
        # Names
        self.first_name_kh = first_name_kh
        self.last_name_kh = last_name_kh
        self.first_name_en = first_name_en
        self.last_name_en = last_name_en
        
        # Gender & DOB
        self.gender = Gender(gender) if isinstance(gender, str) else gender
        self.dob = self._validate_dob(dob)

        # Academic Info
        self.current_grade_level = current_grade_level
        self.current_class_id = current_class_id
        
        # Personal Info
        self.photo_url = photo_url
        self.phone_number = phone_number
        self.address = address or {}
        self.guardians = guardians or []
        
        # Meta
        self.status = StudentStatus(status) if isinstance(status, str) else status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.history: List[Dict[str, Any]] = history or []

    # --- Utility Methods ---
    def touch(self):
        self.updated_at = datetime.utcnow()

    @property
    def full_name_en(self) -> str:
        return f"{self.first_name_en} {self.last_name_en}"

    @property
    def full_name_kh(self) -> str:
        return f"{self.last_name_kh} {self.first_name_kh}"

    # --- Validators (Private) ---
    @staticmethod
    def _age_in_years(dob: date_type, today: Optional[date_type] = None) -> int:
        today = today or date_type.today()
        years = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            years -= 1
        return years

    @classmethod
    def _validate_dob(cls, dob: date_type) -> date_type:
        if not isinstance(dob, date_type):
            raise StudentDobTypeInvalidException(received_type=type(dob).__name__)

        today = date_type.today()
        if dob > today:
            raise StudentDobInFutureException(dob=dob, today=today)

        age = cls._age_in_years(dob, today=today)
        if age < cls.MIN_AGE_YEARS or age > cls.MAX_AGE_YEARS:
            raise StudentAgeOutOfRangeException(
                dob=dob,
                age=age,
                min_age=cls.MIN_AGE_YEARS,
                max_age=cls.MAX_AGE_YEARS,
                today=today,
            )
        return dob

    # --- Business Logic: Profile Updates ---
    def update_profile(self, first_name_en: str, last_name_en: str):
        self.first_name_en = first_name_en
        self.last_name_en = last_name_en
        self.touch()

    def update_dob(self, dob: date_type):
        self.dob = self._validate_dob(dob)
        self.touch()

    def admin_update_general_info(self, payload: Dict[str, Any]):
        """
        Allows Admin to update profile details safely.
        """
        # --- Simple Fields ---
        if "student_id_code" in payload: self.student_id_code = payload["student_id_code"]
        if "first_name_kh" in payload: self.first_name_kh = payload["first_name_kh"]
        if "last_name_kh" in payload: self.last_name_kh = payload["last_name_kh"]
        if "first_name_en" in payload: self.first_name_en = payload["first_name_en"]
        if "last_name_en" in payload: self.last_name_en = payload["last_name_en"]
        
        if "phone_number" in payload: self.phone_number = payload["phone_number"]
        if "address" in payload: self.address = payload["address"]
        if "photo_url" in payload: self.photo_url = payload["photo_url"]
        if "guardians" in payload: self.guardians = payload["guardians"]

        # --- Complex Fields (Enum) ---
        if "gender" in payload:
            val = payload["gender"]
            self.gender = Gender(val) if isinstance(val, str) else val
            
        # --- Complex Fields (Date & Validation) ---
        if "dob" in payload:
            val = payload["dob"]
            if isinstance(val, str):
                try:
                    val = datetime.strptime(val, "%Y-%m-%d").date()
                except ValueError:
                    raise StudentDobStringFormatInvalidException(value=val, expected_format="%Y-%m-%d")
            self.dob = self._validate_dob(val)

        self.touch()

    def _log_history(self, event: str, meta: Optional[Dict[str, Any]] = None):
        self.history.append(
            {
                "event": event,
                "at": datetime.utcnow().isoformat(),
                "meta": meta or {},
            }
        )
    def join_class(self, class_id: ObjectId):
        if self.status != StudentStatus.ACTIVE:
            raise StudentCannotJoinClassWhenNotActiveException(student_id=getattr(self, "id", None), class_id=class_id, status=getattr(self.status, "value", self.status))
        prev_class_id = self.current_class_id
        self.current_class_id = class_id

        self._log_history("CLASS_JOINED",{"from_class_id": str(prev_class_id) if prev_class_id else None,"to_class_id": str(class_id),})
        self.touch()


    def leave_class(self):
        prev_class_id = self.current_class_id
        self.current_class_id = None

        self._log_history("CLASS_LEFT",{"from_class_id": str(prev_class_id) if prev_class_id else None})
        self.touch()
    def promote_grade(self):
        if self.current_grade_level < 12:
            self.current_grade_level += 1
            self.touch()

    # --- Business Logic: Status & Deletion (Soft Delete) ---
    
    def archive(self, reason: str = ""):
        prev_status = self.status
        prev_class_id = self.current_class_id

        self.status = StudentStatus.ARCHIVED
        self.current_class_id = None

        self._log_history("STUDENT_ARCHIVED",{
                "from_status": str(prev_status.value if isinstance(prev_status, StudentStatus) else prev_status),
                "to_status": StudentStatus.ARCHIVED.value,
                "removed_from_class_id": str(prev_class_id) if prev_class_id else None,
                "reason": reason,
            })
        self.touch()

    def restore(self):
        prev_status = self.status

        self.status = StudentStatus.ACTIVE

        self._log_history("STUDENT_RESTORED",{"from_status": str(prev_status.value if isinstance(prev_status, StudentStatus) else prev_status),"to_status": StudentStatus.ACTIVE.value,})
        self.touch()

