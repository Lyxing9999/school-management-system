from __future__ import annotations
from datetime import datetime
from enum import Enum
from bson import ObjectId
from app.contexts.school.errors.enrollment_exceptions import (
    InvalidEnrollmentStatusException,
    EnrollmentAlreadyCompletedException,
    EnrollmentAlreadyDroppedException,
)


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    DROPPED = "dropped"
    COMPLETED = "completed"


class Enrollment:
    """
    Represents a student's enrollment in a given class.
    Useful if you want enrollment history, status, etc.
    """

    def __init__(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
        status: EnrollmentStatus = EnrollmentStatus.ACTIVE,
        id: ObjectId | None = None,
        enrolled_at: datetime | None = None,
        dropped_at: datetime | None = None,
        completed_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        if not isinstance(student_id, ObjectId):
            student_id = ObjectId(student_id)
        if not isinstance(class_id, ObjectId):
            class_id = ObjectId(class_id)

        self.id = id or ObjectId()
        self.student_id = student_id
        self.class_id = class_id
        self._status = self._validate_status(status)
        self.enrolled_at = enrolled_at or datetime.utcnow()
        self.dropped_at = dropped_at
        self.completed_at = completed_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # -------- Properties --------

    @property
    def status(self) -> EnrollmentStatus:
        return self._status

    # -------- Behavior --------

    def mark_dropped(self) -> None:
        if self._status == EnrollmentStatus.COMPLETED:
            raise EnrollmentAlreadyCompletedException(self.id)
        if self._status == EnrollmentStatus.DROPPED:
            raise EnrollmentAlreadyDroppedException(self.id)
        self._status = EnrollmentStatus.DROPPED
        self.dropped_at = datetime.utcnow()
        self._touch()
    def mark_completed(self) -> None:
        if self._status == EnrollmentStatus.DROPPED:
            raise EnrollmentAlreadyDroppedException(self.id)
        if self._status == EnrollmentStatus.COMPLETED:
            raise EnrollmentAlreadyCompletedException(self.id)
        self._status = EnrollmentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self._touch()

    # -------- Internal helpers --------

    def _touch(self) -> None:
        self.updated_at = datetime.utcnow()

    @staticmethod
    def _validate_status(s: EnrollmentStatus | str) -> EnrollmentStatus:
        if isinstance(s, EnrollmentStatus):
            return s

        try:
            return EnrollmentStatus(s)
        except ValueError:
            raise InvalidEnrollmentStatusException(received_value=s)