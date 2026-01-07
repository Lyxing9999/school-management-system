from __future__ import annotations

from datetime import datetime, date as date_type
from enum import Enum
from typing import Optional, List, Dict, Any

from bson import ObjectId

from app.contexts.student.errors.student_exceptions import (
    StudentDobTypeInvalidException,
    StudentDobInFutureException,
    StudentAgeOutOfRangeException,
    StudentDobStringFormatInvalidException,
    StudentCannotJoinClassWhenNotActiveException,
)

from app.contexts.shared.lifecycle.domain import Lifecycle


# --- Enums ---
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


class StudentStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DROPPED_OUT = "dropped_out"
    GRADUATED = "graduated"
    ARCHIVED = "archived"


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
        *,
        id: Optional[ObjectId] = None,
        photo_url: Optional[str] = None,
        phone_number: Optional[str] = None,
        address: Optional[Dict[str, Any]] = None,
        guardians: Optional[List[Dict[str, Any]]] = None,
        status: StudentStatus | str = StudentStatus.ACTIVE,
        lifecycle: Optional[Lifecycle] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
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
        self.current_grade_level = int(current_grade_level)
        self.current_class_id = current_class_id

        # Personal Info
        self.photo_url = photo_url
        self.phone_number = phone_number
        self.address: Dict[str, Any] = address or {}
        self.guardians: List[Dict[str, Any]] = guardians or []

        # Meta
        self.status = StudentStatus(status) if isinstance(status, str) else status
        self.lifecycle = lifecycle or Lifecycle()
        self.history: List[Dict[str, Any]] = history or []

    # --------------------
    # Lifecycle / status helpers
    # --------------------

    def touch(self) -> None:
        self.lifecycle.touch()

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def is_active(self) -> bool:
        # business active + not soft-deleted
        return (not self.is_deleted()) and self.status == StudentStatus.ACTIVE

    @property
    def full_name_en(self) -> str:
        return f"{self.first_name_en} {self.last_name_en}"

    @property
    def full_name_kh(self) -> str:
        return f"{self.last_name_kh} {self.first_name_kh}"

    # --------------------
    # Validators (Private)
    # --------------------

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

    # --------------------
    # Profile updates
    # --------------------

    def update_profile(self, first_name_en: str, last_name_en: str) -> None:
        self.first_name_en = first_name_en
        self.last_name_en = last_name_en
        self.touch()

    def update_dob(self, dob: date_type) -> None:
        self.dob = self._validate_dob(dob)
        self.touch()

    def admin_update_general_info(self, payload: Dict[str, Any]) -> None:
        """
        Allows Admin to update profile details safely.
        """
        # --- Simple Fields ---
        if "student_id_code" in payload:
            self.student_id_code = payload["student_id_code"]
        if "first_name_kh" in payload:
            self.first_name_kh = payload["first_name_kh"]
        if "last_name_kh" in payload:
            self.last_name_kh = payload["last_name_kh"]
        if "first_name_en" in payload:
            self.first_name_en = payload["first_name_en"]
        if "last_name_en" in payload:
            self.last_name_en = payload["last_name_en"]

        if "phone_number" in payload:
            self.phone_number = payload["phone_number"]
        if "address" in payload:
            self.address = payload["address"] or {}
        if "photo_url" in payload:
            self.photo_url = payload["photo_url"]
        if "guardians" in payload:
            self.guardians = payload["guardians"] or []

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

    # --------------------
    # History + status transitions
    # --------------------

    def _log_history(self, event: str, meta: Optional[Dict[str, Any]] = None) -> None:
        self.history.append(
            {
                "event": event,
                "at": datetime.utcnow().isoformat(),
                "meta": meta or {},
            }
        )

    def _set_status(
        self,
        new_status: StudentStatus,
        *,
        reason: str = "",
        actor_id: ObjectId | None = None,
    ) -> None:
        prev_status = self.status
        if prev_status == new_status:
            return

        self.status = new_status

        self._log_history(
            "STUDENT_STATUS_CHANGED",
            {
                "from_status": prev_status.value if isinstance(prev_status, StudentStatus) else str(prev_status),
                "to_status": new_status.value,
                "reason": reason,
                "actor_id": str(actor_id) if actor_id else None,
            },
        )
        self.touch()

    # --------------------
    # Enrollment behavior
    # --------------------

    def join_class(self, class_id: ObjectId) -> None:
        if not self.is_active():
            raise StudentCannotJoinClassWhenNotActiveException(
                student_id=getattr(self, "id", None),
                class_id=class_id,
                status=getattr(self.status, "value", self.status),
            )

        prev_class_id = self.current_class_id
        self.current_class_id = class_id

        self._log_history(
            "CLASS_JOINED",
            {
                "from_class_id": str(prev_class_id) if prev_class_id else None,
                "to_class_id": str(class_id),
            },
        )
        self.touch()

    def leave_class(self) -> None:
        prev_class_id = self.current_class_id
        self.current_class_id = None

        self._log_history(
            "CLASS_LEFT",
            {
                "from_class_id": str(prev_class_id) if prev_class_id else None,
            },
        )
        self.touch()

    def promote_grade(self) -> None:
        if self.current_grade_level < 12:
            self.current_grade_level += 1
            self.touch()

    # --------------------
    # Business status methods (full flow)
    # --------------------

    def suspend(self, reason: str = "", actor_id: ObjectId | None = None) -> None:
        self._set_status(StudentStatus.SUSPENDED, reason=reason, actor_id=actor_id)

    def drop_out(self, reason: str = "", actor_id: ObjectId | None = None) -> None:
        prev_class_id = self.current_class_id
        self.current_class_id = None

        self._log_history(
            "STUDENT_DROPPED_OUT",
            {
                "removed_from_class_id": str(prev_class_id) if prev_class_id else None,
                "reason": reason,
                "actor_id": str(actor_id) if actor_id else None,
            },
        )
        self._set_status(StudentStatus.DROPPED_OUT, reason=reason, actor_id=actor_id)

    def graduate(self, reason: str = "", actor_id: ObjectId | None = None) -> None:
        prev_class_id = self.current_class_id
        self.current_class_id = None

        self._log_history(
            "STUDENT_GRADUATED",
            {
                "removed_from_class_id": str(prev_class_id) if prev_class_id else None,
                "reason": reason,
                "actor_id": str(actor_id) if actor_id else None,
            },
        )
        self._set_status(StudentStatus.GRADUATED, reason=reason, actor_id=actor_id)

    def archive(self, reason: str = "", actor_id: ObjectId | None = None) -> None:
        prev_class_id = self.current_class_id
        self.current_class_id = None

        self._log_history(
            "STUDENT_ARCHIVED",
            {
                "removed_from_class_id": str(prev_class_id) if prev_class_id else None,
                "reason": reason,
                "actor_id": str(actor_id) if actor_id else None,
            },
        )
        self._set_status(StudentStatus.ARCHIVED, reason=reason, actor_id=actor_id)

    def restore(self, reason: str = "", actor_id: ObjectId | None = None) -> None:
        # restore back to ACTIVE (business restore)
        self._set_status(StudentStatus.ACTIVE, reason=reason, actor_id=actor_id)