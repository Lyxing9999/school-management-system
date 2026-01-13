
from typing import Optional
from bson import ObjectId

from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.errors.grade_exceptions import GradeNotFoundException
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException  # or your own exception

from ._base import OidMixin


class GradeService(OidMixin):
    def __init__(self, *, grade_repo, grade_factory, grade_policy, grade_lifecycle):
        self.grade_repo = grade_repo
        self.grade_factory = grade_factory
        self.grade_policy = grade_policy
        self.grade_lifecycle = grade_lifecycle

    def add_grade(
        self,
        student_id: str | ObjectId,
        subject_id: str | ObjectId,
        score: float,
        type: GradeType | str,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId | None = None,
        term: str | None = None,
        *,
        require_student_in_class: bool = False,
        prevent_duplicate: bool = False,
    ) -> GradeRecord:

        can = self.grade_policy.can_create(
            student_id=self._oid(student_id),
            subject_id=self._oid(subject_id),
            teacher_id=self._oid(teacher_id),
            class_id=self._oid(class_id) if class_id else None,
            term=term,
            grade_type=str(type),  
            require_student_in_class=require_student_in_class,
            prevent_duplicate=prevent_duplicate,
            allow_homeroom_override=False,
        )
        if not can.allowed:

            raise LifecyclePolicyDeniedException(
                entity="grade",
                entity_id="(new)",
                mode=can.mode,
                reasons=can.reasons,
                recommended=can.recommended,
            )

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

    def update_grade_score(
        self,
        grade_id: str | ObjectId,
        new_score: float,
        *,
        actor_teacher_id: str | ObjectId,
    ) -> Optional[GradeRecord]:
        oid = self._oid(grade_id)
        actor_oid = self._oid(actor_teacher_id)

        can = self.grade_policy.can_update(oid, actor_oid)
        if not can.allowed:
            raise LifecyclePolicyDeniedException(
                entity="grade",
                entity_id=str(oid),
                mode=can.mode,
                reasons=can.reasons,
                recommended=can.recommended,
            )

        existing = self.grade_repo.find_by_id(oid)
        if existing is None:
            raise GradeNotFoundException(str(grade_id))

        existing.set_score(new_score)
        return self.grade_repo.update(existing)

    def change_grade_type(
        self,
        grade_id: str | ObjectId,
        new_type: GradeType | str,
        *,
        actor_teacher_id: str | ObjectId | None = None,
    ) -> Optional[GradeRecord]:
        oid = self._oid(grade_id)

        can = self.grade_policy.can_update(oid, actor_teacher_id)
        if not can.allowed:
            raise LifecyclePolicyDeniedException(
                entity="grade",
                entity_id=str(oid),
                mode=can.mode,
                reasons=can.reasons,
                recommended=can.recommended,
            )

        existing = self.grade_repo.find_by_id(oid)
        if existing is None:
            raise GradeNotFoundException(str(grade_id))

        existing.change_type(new_type)
        return self.grade_repo.update(existing)

    def get_grade_by_id(self, grade_id: str | ObjectId) -> Optional[GradeRecord]:
        return self.grade_repo.find_by_id(self._oid(grade_id))


    def soft_delete_grade(self, grade_id: str | ObjectId, actor_teacher_id: str | ObjectId) -> int:
        res = self.grade_lifecycle.soft_delete_grade(self._oid(grade_id), self._oid(actor_teacher_id))
        return int(res.modified_count)

    def restore_grade(self, grade_id: str | ObjectId, actor_teacher_id: str | ObjectId | None = None) -> int:
        res = self.grade_lifecycle.restore_grade(self._oid(grade_id), self._oid(actor_teacher_id) if actor_teacher_id else None)
        return int(res.modified_count)

    def hard_delete_grade(self, grade_id: str | ObjectId, actor_teacher_id: str | ObjectId) -> int:
        res = self.grade_lifecycle.hard_delete_grade(self._oid(grade_id), self._oid(actor_teacher_id))
        return int(res.deleted_count)