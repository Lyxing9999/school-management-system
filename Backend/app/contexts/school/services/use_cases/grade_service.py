from __future__ import annotations

from typing import Optional
from bson import ObjectId

from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.errors.grade_exceptions import GradeNotFoundException

from ._base import OidMixin


class GradeService(OidMixin):
    def __init__(self, *, grade_repo, grade_factory):
        self.grade_repo = grade_repo
        self.grade_factory = grade_factory

    def add_grade(
        self,
        student_id: str | ObjectId,
        subject_id: str | ObjectId,
        score: float,
        type: GradeType | str,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId | None = None,
        term: str | None = None,
    ) -> GradeRecord:
        grade = self.grade_factory.create_grade(
            student_id=student_id,
            subject_id=subject_id,
            score=score,
            type=type,
            teacher_id=teacher_id,
            class_id=class_id,
            term=term,
        )
        return self.grade_repo.insert(grade)

    def update_grade_score(self, grade_id: str | ObjectId, new_score: float) -> Optional[GradeRecord]:
        oid = self._oid(grade_id)
        existing = self.grade_repo.find_by_id(oid)
        if existing is None:
            raise GradeNotFoundException(grade_id)

        existing.set_score(new_score)
        return self.grade_repo.update(existing)

    def change_grade_type(self, grade_id: str | ObjectId, new_type: GradeType | str) -> Optional[GradeRecord]:
        oid = self._oid(grade_id)
        existing = self.grade_repo.find_by_id(oid)
        if existing is None:
            raise GradeNotFoundException(grade_id)

        existing.change_type(new_type)
        return self.grade_repo.update(existing)

    def get_grade_by_id(self, grade_id: str | ObjectId) -> Optional[GradeRecord]:
        return self.grade_repo.find_by_id(self._oid(grade_id))