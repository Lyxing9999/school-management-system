from __future__ import annotations
from typing import Iterable

from app.contexts.school.domain.subject import Subject
from app.contexts.school.errors.subject_exceptions import (
    SubjectCodeAlreadyExistsException,
    SubjectNameAlreadyExistsException,
)


class SubjectFactory:
    """
    Factory for creating Subject entities with basic validation.

    Responsibilities:
    - Validate unique subject code
    - (Optionally) validate unique name
    - Normalize grade levels
    """

    def __init__(self, subject_read_model):
        """
        :param subject_read_model: provides methods like:
            - get_by_code(code) -> dict | None
            - get_by_name(name) -> dict | None
        """
        self.subject_read_model = subject_read_model

    def create_subject(
        self,
        name: str,
        code: str,
        description: str | None = None,
        allowed_grade_levels: Iterable[int] | None = None,
    ) -> Subject:
        normalized_code = code.strip().upper()
        normalized_name = name.strip()

        # 1. Validate uniqueness
        if self.subject_read_model.get_by_code(normalized_code):
            raise SubjectCodeAlreadyExistsException(normalized_code)

        if self.subject_read_model.get_by_name(normalized_name):
            raise SubjectNameAlreadyExistsException(normalized_name)

        # 2. Create domain model (Subject will validate grade levels itself)
        return Subject(
            name=normalized_name,
            code=normalized_code,
            description=description,
            allowed_grade_levels=allowed_grade_levels or [],
        )