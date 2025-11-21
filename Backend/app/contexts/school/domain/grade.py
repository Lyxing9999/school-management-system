from __future__ import annotations
from datetime import datetime
from enum import Enum
from bson import ObjectId
from app.contexts.school.errors.grade_exceptions import (
    InvalidGradeTypeException,
    InvalidGradeScoreException,
    GradeTypeChangeForbiddenException
)

class GradeType(str, Enum):
    EXAM = "exam"
    ASSIGNMENT = "assignment"


class GradeRecord:
    """
    Represents a single grade entry (e.g., exam or assignment score).
    """

    def __init__(
        self,
        student_id: ObjectId,
        subject_id: ObjectId,
        score: float,
        type: GradeType,
        id: ObjectId | None = None,
        class_id: ObjectId | None = None,
        teacher_id: ObjectId | None = None,
        term: str | None = None,  # e.g. "2025-S1"
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        if not isinstance(student_id, ObjectId):
            student_id = ObjectId(student_id)
        if not isinstance(subject_id, ObjectId):
            subject_id = ObjectId(subject_id)
        if class_id is not None and not isinstance(class_id, ObjectId):
            class_id = ObjectId(class_id)
        if teacher_id is not None and not isinstance(teacher_id, ObjectId):
            teacher_id = ObjectId(teacher_id)

        self.id = id or ObjectId()
        self.student_id = student_id
        self.subject_id = subject_id
        self.class_id = class_id
        self.teacher_id = teacher_id
        self.term = term
        self._type = self._validate_type(type)
        self._score: float = 0.0
        self.set_score(score)
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # -------- Properties --------

    @property
    def type(self) -> GradeType:
        return self._type

    @property
    def score(self) -> float:
        return self._score

    # -------- Behavior --------

    def set_score(self, value: float) -> None:
        """Validate and update score (0–100)."""
        if value < 0 or value > 100:
            raise InvalidGradeScoreException(score=value)
        self._score = float(value)
        self._touch()

    def change_type(self, new_type: GradeType) -> None:
        if self._score > 0:
            raise GradeTypeChangeForbiddenException(grade_id=str(self.id))
        self._type = self._validate_type(new_type)
        self._touch()

    # -------- Internal helpers --------
    def _touch(self) -> None:
        self.updated_at = datetime.utcnow()
    @staticmethod
    def _validate_type(t: GradeType | str) -> GradeType:
        if isinstance(t, GradeType):
            return t
        try:
            return GradeType(t)
        except ValueError:
            raise InvalidGradeTypeException(received_value=t)