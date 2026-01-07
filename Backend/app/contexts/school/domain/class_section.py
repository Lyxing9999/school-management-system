from __future__ import annotations

from enum import Enum
from typing import Iterable, List, Optional
from bson import ObjectId

from app.contexts.shared.lifecycle.domain import Lifecycle, now_utc
from app.contexts.school.errors.class_exceptions import (
    InvalidClassSectionNameError,
    ClassSectionFullException,
    InvalidMaxStudentsError,
    InvalidSubjectIdError,
    InvalidTeacherIdError,
    StudentCapacityExceededError,
    ClassSectionDeletedException,  
    InvalidClassSectionStatusError, 
    ClassSectionNotActiveException,
)


class ClassSectionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ClassSection:
    """
    Aggregate root representing a class/section.

    - lifecycle = soft delete + audit timestamps (UTC)
    - status = business status (active/inactive/archived)
    """

    def __init__(
        self,
        name: str,
        *,
        id: Optional[ObjectId] = None,
        homeroom_teacher_id: Optional[ObjectId] = None,
        subject_ids: Optional[Iterable[ObjectId]] = None,
        enrolled_count: Optional[int] = 0,
        max_students: Optional[int] = None,
        status: ClassSectionStatus | str = ClassSectionStatus.ACTIVE,
        lifecycle: Lifecycle | None = None,
    ) -> None:
        if not name or not name.strip():
            raise InvalidClassSectionNameError(received_value=name)

        self.id = id or ObjectId()
        self._name = name.strip()
        self._homeroom_teacher_id = homeroom_teacher_id
        self._subject_ids: List[ObjectId] = list(subject_ids or [])

        self._enrolled_count = enrolled_count if enrolled_count is not None else 0
        self._max_students = max_students if max_students is not None else 30

        self.status = self._validate_status(status)
        self.lifecycle = lifecycle or Lifecycle()

        self._validate_student_capacity()

    # -------- Properties --------

    @property
    def name(self) -> str:
        return self._name

    @property
    def homeroom_teacher_id(self) -> ObjectId | None:
        return self._homeroom_teacher_id

    @property
    def enrolled_count(self) -> int:
        return self._enrolled_count

    @property
    def subject_ids(self) -> tuple[ObjectId, ...]:
        return tuple(self._subject_ids)

    @property
    def max_students(self) -> int:
        return self._max_students

    # -------- Lifecycle helpers --------

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def soft_delete(self, actor_id: ObjectId) -> None:
        self.lifecycle.soft_delete(actor_id)

    def restore(self) -> None:
        self.lifecycle.restore()

    # -------- Business status helpers --------

    def is_active(self) -> bool:
        # Active means: not deleted AND status == ACTIVE
        return (not self.is_deleted()) and self.status == ClassSectionStatus.ACTIVE

    def is_archived(self) -> bool:
        return self.status == ClassSectionStatus.ARCHIVED

    # -------- Behavior / business rules --------

    def rename(self, new_name: str) -> None:
        self._require_not_deleted()
        if not new_name or not new_name.strip():
            raise InvalidClassSectionNameError(received_value=new_name)
        self._name = new_name.strip()
        self._touch()

    def assign_homeroom_teacher(self, homeroom_teacher_id: ObjectId) -> None:
        self._require_not_deleted()
        if not isinstance(homeroom_teacher_id, ObjectId):
            raise InvalidTeacherIdError(received_value=homeroom_teacher_id)
        self._homeroom_teacher_id = homeroom_teacher_id
        self._touch()

    def remove_homeroom_teacher(self) -> None:
        self._require_not_deleted()
        self._homeroom_teacher_id = None
        self._touch()

    def increment_enrollment(self) -> None:
        self._require_not_deleted()
        if self.status != ClassSectionStatus.ACTIVE:
            raise ClassSectionNotActiveException()

        if self._enrolled_count >= self._max_students:
            raise ClassSectionFullException()

        self._enrolled_count += 1
        self._touch()

    def decrement_enrollment(self) -> None:
        self._require_not_deleted()
        if self._enrolled_count > 0:
            self._enrolled_count -= 1
        self._touch()

    def set_max_students(self, max_students: int) -> None:
        self._require_not_deleted()
        if max_students <= 0:
            raise InvalidMaxStudentsError(received_value=max_students)
        self._max_students = max_students
        self._validate_student_capacity()
        self._touch()

    def set_status(self, status: ClassSectionStatus | str) -> None:
        self._require_not_deleted()
        self.status = self._validate_status(status)
        self._touch()

    def add_subject(self, subject_id: ObjectId) -> None:
        self._require_not_deleted()
        if not isinstance(subject_id, ObjectId):
            raise InvalidSubjectIdError(received_value=subject_id)
        if subject_id not in self._subject_ids:
            self._subject_ids.append(subject_id)
            self._touch()

    def remove_subject(self, subject_id: ObjectId) -> None:
        self._require_not_deleted()
        if not isinstance(subject_id, ObjectId):
            raise InvalidSubjectIdError(received_value=subject_id)
        if subject_id in self._subject_ids:
            self._subject_ids.remove(subject_id)
            self._touch()

    # -------- Internal helpers --------

    def _touch(self) -> None:
        self.lifecycle.touch(now_utc())

    def _require_not_deleted(self) -> None:
        if self.is_deleted():
            raise ClassSectionDeletedException(self.id)

    @staticmethod
    def _validate_status(status: ClassSectionStatus | str) -> ClassSectionStatus:
        if isinstance(status, ClassSectionStatus):
            return status
        try:
            return ClassSectionStatus(status)
        except ValueError:
            raise InvalidClassSectionStatusError(received_value=status)

    def _validate_student_capacity(self) -> None:
        if self._enrolled_count > self._max_students:
            raise StudentCapacityExceededError(
                class_name=self._name,
                max_students=self._max_students,
                current_count=self._enrolled_count,
            )