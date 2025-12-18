from __future__ import annotations
from datetime import datetime
from typing import Iterable, List, Optional
from bson import ObjectId

from app.contexts.school.errors.class_exceptions import (
    InvalidClassSectionNameError,
    ClassSectionFullException,
    InvalidMaxStudentsError,
    InvalidSubjectIdError,
    InvalidTeacherIdError,
    StudentCapacityExceededError
)

class ClassSection:
    """
    Aggregate root representing a class/section in the school.
    Links a teacher, students and subjects together.
    """
    def __init__(
        self,
        name: str,
        id: Optional[ObjectId] = None,
        teacher_id: Optional[ObjectId] = None,
        subject_ids: Optional[Iterable[ObjectId]] = None,
        enrolled_count: Optional[int] = 0, 
        max_students: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted: bool = False,
    ):
        if not name or not name.strip():
            raise InvalidClassSectionNameError(received_value=name)

        self.id = id or ObjectId()
        self._name = name.strip()
        self._teacher_id = teacher_id
        self._subject_ids: List[ObjectId] = list(subject_ids or [])
        

        self._enrolled_count = enrolled_count if enrolled_count is not None else 0
        self._max_students = max_students or 30

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted

        # Validate after setting everything
        self._validate_student_capacity()

    # -------- Properties --------

    @property
    def name(self) -> str:
        return self._name

    @property
    def teacher_id(self) -> ObjectId | None:
        return self._teacher_id

    @property
    def enrolled_count(self) -> int:
        return self._enrolled_count

    @property
    def subject_ids(self) -> tuple[ObjectId, ...]:
        return tuple(self._subject_ids)

    @property
    def max_students(self) -> int | None:
        return self._max_students

    # -------- Behavior / business rules --------

    def rename(self, new_name: str) -> None:
        if not new_name or not new_name.strip():
            raise InvalidClassSectionNameError(received_value=new_name)
        self._name = new_name.strip()
        self._touch()

    def assign_teacher(self, teacher_id: ObjectId) -> None:
        if not isinstance(teacher_id, ObjectId):
            raise InvalidTeacherIdError(received_value=teacher_id)

        self._teacher_id = teacher_id
        self._touch()

    def remove_teacher(self) -> None:
        self._teacher_id = None
        self._touch()

    def increment_enrollment(self):
        # Fix 3: Use _enrolled_count (backing field) instead of property
        # Also check capacity BEFORE incrementing
        if self._max_students is not None and self._enrolled_count >= self._max_students:
            raise ClassSectionFullException()
        
        self._enrolled_count += 1
        self._touch()

    def decrement_enrollment(self):
        # Fix 4: Use _enrolled_count and _touch()
        if self._enrolled_count > 0:
            self._enrolled_count -= 1
        self._touch() 

    def set_max_students(self, max_students: int | None) -> None:
        if max_students is not None and max_students <= 0:
            raise InvalidMaxStudentsError(received_value=max_students)

        self._max_students = max_students
        # If we lower the max limit below current count, this validation will raise Error
        self._validate_student_capacity() 
        self._touch()

    def add_subject(self, subject_id: ObjectId) -> None:
        if not isinstance(subject_id, ObjectId):
            raise InvalidSubjectIdError(received_value=subject_id)

        if subject_id not in self._subject_ids:
            self._subject_ids.append(subject_id)
            self._touch()

    def remove_subject(self, subject_id: ObjectId) -> None:
        if not isinstance(subject_id, ObjectId):
            raise InvalidSubjectIdError(received_value=subject_id)

        if subject_id in self._subject_ids:
            self._subject_ids.remove(subject_id)
            self._touch()

    def soft_delete(self) -> None:
        self.deleted = True
        self._touch()

    # -------- Internal helpers --------

    def _touch(self) -> None:
        self.updated_at = datetime.utcnow()

    def _validate_student_capacity(self) -> None:
        current = self._enrolled_count or 0
        if self._max_students is not None and current > self._max_students:
            raise StudentCapacityExceededError(
                class_name=self._name, 
                max_students=self._max_students, 
                current_count=current
            )