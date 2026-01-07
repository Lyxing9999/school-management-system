from __future__ import annotations

from typing import Iterable
from bson import ObjectId

from app.contexts.shared.lifecycle.domain import Lifecycle, now_utc
from app.contexts.school.errors.subject_exceptions import (
    InvalidSubjectNameError,
    InvalidSubjectCodeError,
    InvalidGradeLevelError,
    SubjectDeletedException, 
    SubjectPatchFieldNotAllowedException,
    SubjectNoChangeException,
)


class Subject:
    """
    Reference data: school subject (Math, Physics, ...)

    Notes:
    - lifecycle timestamps are UTC
    - is_active is BUSINESS status (can be inactive but not deleted)
    - soft delete is for "removed from system" or "undo"
    """

    def __init__(
        self,
        name: str,
        code: str,
        *,
        id: ObjectId | None = None,
        description: str | None = None,
        allowed_grade_levels: Iterable[int] | None = None,
        is_active: bool = True,
        lifecycle: Lifecycle | None = None,
    ) -> None:
        if not name or not name.strip():
            raise InvalidSubjectNameError(received_value=name)
        if not code or not code.strip():
            raise InvalidSubjectCodeError(received_value=code)

        self.id = id or ObjectId()
        self._name = name.strip()
        self._code = code.strip().upper()
        self._description = description
        self._allowed_grade_levels: list[int] = self._normalize_grade_levels(allowed_grade_levels or [])
        self.is_active = bool(is_active)

        self.lifecycle = lifecycle or Lifecycle()

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

    # -------- Lifecycle helpers --------

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def soft_delete(self, actor_id: ObjectId) -> None:
        self.lifecycle.soft_delete(actor_id)

    def restore(self) -> None:
        self.lifecycle.restore()

    # -------- Behavior --------

    def rename(self, new_name: str) -> None:
        self._require_not_deleted()
        if not new_name or not new_name.strip():
            raise InvalidSubjectNameError(received_value=new_name)
        self._name = new_name.strip()
        self._touch()

    def change_code(self, new_code: str) -> None:
        self._require_not_deleted()
        if not new_code or not new_code.strip():
            raise InvalidSubjectCodeError(received_value=new_code)
        self._code = new_code.strip().upper()
        self._touch()

    def update_description(self, description: str | None) -> None:
        self._require_not_deleted()
        self._description = description
        self._touch()

    def set_allowed_grade_levels(self, levels: Iterable[int]) -> None:
        self._require_not_deleted()
        self._allowed_grade_levels = self._normalize_grade_levels(levels)
        self._touch()

    def deactivate(self) -> None:
        self._require_not_deleted()
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        self._require_not_deleted()
        self.is_active = True
        self._touch()

    # -------- Internal helpers --------

    def _touch(self) -> None:
        self.lifecycle.touch(now_utc())

    def _require_not_deleted(self) -> None:
        if self.is_deleted():
            raise SubjectDeletedException(self.id)

    @staticmethod
    def _normalize_grade_levels(levels: Iterable[int]) -> list[int]:
        unique_sorted = sorted(set(levels))
        for level in unique_sorted:
            if level < 1 or level > 12:
                raise InvalidGradeLevelError(level)
        return unique_sorted



    def apply_patch(
        self,
        *,
        name: str | None = None,
        code: str | None = None,
        description: str | None = None,
        allowed_grade_levels: list[int] | None = None,
        is_active: bool | None = None,
    ) -> None:
        self._require_not_deleted()

        changed = False

        if name is not None:
            new_name = name.strip()
            if new_name != self._name:
                self.rename(new_name)
                changed = True

        if code is not None:
            new_code = code.strip().upper()
            if new_code != self._code:
                self.change_code(new_code)
                changed = True

        if description is not None:
            if description != self._description:
                self.update_description(description)
                changed = True

        if allowed_grade_levels is not None:
            # PATCH not allowed to change grade levels
            raise SubjectPatchFieldNotAllowedException("allowed_grade_levels")

        if is_active is not None:
            if is_active != self.is_active:
                self.activate() if is_active else self.deactivate()
                changed = True

        if not changed:
            raise SubjectNoChangeException(self.id)