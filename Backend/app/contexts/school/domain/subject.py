from __future__ import annotations
from datetime import datetime
from typing import Iterable
from bson import ObjectId
from app.contexts.school.errors.subject_exceptions import (
    InvalidSubjectNameError,
    InvalidSubjectCodeError,
    InvalidGradeLevelError
)

class Subject:
    """
    Represents a school subject (e.g., Math, Physics).
    Often used as reference data, but can still have rules.
    """

    def __init__(
        self,
        name: str,
        code: str,
        id: ObjectId | None = None,
        description: str | None = None,
        allowed_grade_levels: Iterable[int] | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        if not name or not name.strip():
            raise InvalidSubjectNameError(received_value=name)
        if not code or not code.strip():
            raise InvalidSubjectCodeError(received_value=code)

        self.id = id or ObjectId()
        self._name = name.strip()
        self._code = code.strip().upper()
        self._description = description
        self._allowed_grade_levels: list[int] = self._normalize_grade_levels(
            allowed_grade_levels or []
        )
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # -------- Properties --------

    @property
    def name(self) -> str:
        return self._name

    @property
    def code(self) -> str:
        return self._code

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def allowed_grade_levels(self) -> tuple[int, ...]:
        return tuple(self._allowed_grade_levels)

    # -------- Behavior --------

    def rename(self, new_name: str) -> None:
        if not new_name or not new_name.strip():
            raise InvalidSubjectNameError(received_value=new_name)
        self._name = new_name.strip()
        self._touch()

    def change_code(self, new_code: str) -> None:
        if not new_code or not new_code.strip():
            raise InvalidSubjectCodeError(received_value=new_code)
        self._code = new_code.strip().upper()
        self._touch()

    def update_description(self, description: str | None) -> None:
        self._description = description
        self._touch()

    def set_allowed_grade_levels(self, levels: Iterable[int]) -> None:
        self._allowed_grade_levels = self._normalize_grade_levels(levels)
        self._touch()

    def deactivate(self) -> None:
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        self.is_active = True
        self._touch()

    # -------- Internal helpers --------

    def _touch(self) -> None:
        self.updated_at = datetime.utcnow()

    @staticmethod
    def _normalize_grade_levels(levels: Iterable[int]) -> list[int]:
        unique_sorted = sorted(set(levels))
        for level in unique_sorted:
            if level < 1 or level > 12:
                raise InvalidGradeLevelError(level)
        return unique_sorted