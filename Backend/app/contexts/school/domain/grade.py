from __future__ import annotations

import re
from enum import Enum
from bson import ObjectId

from app.contexts.shared.lifecycle.domain import Lifecycle, now_utc
from app.contexts.school.errors.grade_exceptions import (
    InvalidGradeTypeException,
    InvalidGradeScoreException,
    GradeTypeChangeForbiddenException,
    GradeRecordDeletedException,
    InvalidTermException,
)

# Accept: 2025-S1 or 2025-S2
_TERM_RE = re.compile(r"^(?P<year>\d{4})-(?P<semester>S[12])$")


class GradeType(str, Enum):
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    HOMEWORK = "homework"
    QUIZ = "quiz"


class GradeRecord:
    """
    Represents a single grade entry (e.g., exam or assignment score).

    Invariants:
    - score is 0..100
    - type is one of GradeType
    - term must be None or 'YYYY-S1'/'YYYY-S2'
    - lifecycle timestamps are UTC
    """

    def __init__(
        self,
        student_id: ObjectId | str,
        subject_id: ObjectId | str,
        score: float,
        type: GradeType | str,
        *,
        id: ObjectId | None = None,
        class_id: ObjectId | str | None = None,
        teacher_id: ObjectId | str | None = None,
        term: str | None = None,  # e.g. "2025-S1"
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self.id = id or ObjectId()

        self.student_id = self._oid(student_id, field="student_id")
        self.subject_id = self._oid(subject_id, field="subject_id")
        self.class_id = self._oid_optional(class_id, field="class_id")
        self.teacher_id = self._oid_optional(teacher_id, field="teacher_id")

        self.term = self._validate_term(term)

        self._type = self._validate_type(type)
        self._score: float = 0.0

        self.lifecycle = lifecycle or Lifecycle()

        # will touch updated_at
        self.set_score(score)

    # ---------------- Properties ----------------

    @property
    def type(self) -> GradeType:
        return self._type

    @property
    def score(self) -> float:
        return self._score

    # ---------------- Lifecycle ----------------

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def soft_delete(self, actor_id: ObjectId) -> None:
        # business decision: allow soft delete even if already deleted -> lifecycle returns False/True
        self.lifecycle.soft_delete(actor_id, now_utc())

    def restore(self) -> None:
        self.lifecycle.restore(now_utc())

    # ---------------- Behavior ----------------

    def set_score(self, value: float) -> None:
        if self.is_deleted():
            raise GradeRecordDeletedException(str(self.id))

        try:
            v = float(value)
        except (TypeError, ValueError):
            raise InvalidGradeScoreException(score=value)

        if v < 0 or v > 100:
            raise InvalidGradeScoreException(score=v)

        self._score = v
        self._touch()

    def change_type(self, new_type: GradeType | str) -> None:
        if self.is_deleted():
            raise GradeRecordDeletedException(str(self.id))

        # your rule: forbid type change once a score exists (>0)
        if self._score > 0:
            raise GradeTypeChangeForbiddenException(grade_id=str(self.id))

        self._type = self._validate_type(new_type)
        self._touch()

    def set_term(self, term: str | None) -> None:
        """
        Optional: allow changing term (admin operation).
        """
        if self.is_deleted():
            raise GradeRecordDeletedException(str(self.id))

        self.term = self._validate_term(term)
        self._touch()

    # ---------------- Internal ----------------

    def _touch(self) -> None:
        self.lifecycle.touch(now_utc())

    @staticmethod
    def _validate_type(t: GradeType | str) -> GradeType:
        if isinstance(t, GradeType):
            return t
        try:
            return GradeType(t)
        except ValueError:
            raise InvalidGradeTypeException(received_value=t)

    @staticmethod
    def _validate_term(term: str | None) -> str | None:
        if term is None:
            return None

        t = term.strip().upper()
        if t == "":
            return None

        m = _TERM_RE.match(t)
        if not m:
            raise InvalidTermException(received_value=term, expected="YYYY-S1 or YYYY-S2")

        year = int(m.group("year"))
        if year < 2000 or year > 2100:
            raise InvalidTermException(received_value=term, expected="year must be 2000..2100")

        return t

    @staticmethod
    def _oid(value: ObjectId | str, *, field: str) -> ObjectId:
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(value)
        except Exception:
            # keep it simple; your AppBaseException can wrap it if you want
            raise ValueError(f"Invalid ObjectId for {field}: {value}")

    @staticmethod
    def _oid_optional(value: ObjectId | str | None, *, field: str) -> ObjectId | None:
        if value is None:
            return None
        return GradeRecord._oid(value, field=field)