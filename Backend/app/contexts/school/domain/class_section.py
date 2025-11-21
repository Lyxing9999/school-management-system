# app/contexts/school/domain/class_section.py
from __future__ import annotations
from datetime import datetime
from typing import Iterable
from bson import ObjectId

from app.contexts.school.errors.class_exceptions import (
    InvalidClassSectionNameError,
    StudentCapacityExceededError,
    InvalidMaxStudentsError,
    DuplicateStudentEnrollmentError,
    InvalidSubjectIdError,
    InvalidTeacherIdError,
)


class ClassSection:
    """
    Aggregate root representing a class/section in the school.
    Links a teacher, students and subjects together.
    """
    def __init__(
        self,
        name: str,
        id: ObjectId | None = None,
        teacher_id: ObjectId | None = None,
        student_ids: Iterable[ObjectId] | None = None,
        subject_ids: Iterable[ObjectId] | None = None,
        max_students: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        deleted: bool = False,
    ):
        if not name or not name.strip():
            raise InvalidClassSectionNameError(received_value=name)

        self.id = id or ObjectId()
        self._name = name.strip()
        self._teacher_id = teacher_id
        self._student_ids: list[ObjectId] = list(student_ids or [])
        self._subject_ids: list[ObjectId] = list(subject_ids or [])
        self._max_students = max_students

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted

        self._validate_student_capacity()

    # -------- Properties --------

    @property
    def name(self) -> str:
        return self._name

    @property
    def teacher_id(self) -> ObjectId | None:
        return self._teacher_id

    @property
    def student_ids(self) -> tuple[ObjectId, ...]:
        return tuple(self._student_ids)

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

    def enroll_student(self, student_id: ObjectId) -> None:
        if not isinstance(student_id, ObjectId):
            raise InvalidTeacherIdError(received_value=student_id)

        if student_id in self._student_ids:
            raise DuplicateStudentEnrollmentError(
                student_id=student_id,
                class_id=self.id,
            )

        self._student_ids.append(student_id)
        self._validate_student_capacity()
        self._touch()

    def unenroll_student(self, student_id: ObjectId) -> None:
        if not isinstance(student_id, ObjectId):
            raise InvalidTeacherIdError(received_value=student_id)

        if student_id in self._student_ids:
            self._student_ids.remove(student_id)
            self._touch()

    def set_max_students(self, max_students: int | None) -> None:
        if max_students is not None and max_students <= 0:
            raise InvalidMaxStudentsError(received_value=max_students)

        self._max_students = max_students
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
        if (
            self._max_students is not None
            and len(self._student_ids) > self._max_students
        ):
            raise StudentCapacityExceededError(
                class_name=self._name,
                max_students=self._max_students,
                current_count=len(self._student_ids),
            )
