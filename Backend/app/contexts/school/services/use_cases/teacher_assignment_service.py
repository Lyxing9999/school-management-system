from __future__ import annotations

from bson import ObjectId

from app.contexts.school.errors.class_exceptions import ClassNotFoundException
from app.contexts.school.errors.subject_exceptions import SubjectNotFoundException

from ._base import OidMixin


class TeacherAssignmentService(OidMixin):
    def __init__(self, *, class_repo, subject_repo, teacher_assignment_repo):
        self.class_repo = class_repo
        self.subject_repo = subject_repo
        self.teacher_assignment_repo = teacher_assignment_repo

    def assign_teacher_to_subject_in_class(
        self,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId,
        subject_id: str | ObjectId,
        actor_id: str | ObjectId | None = None,
    ) -> bool:
        teacher_oid = self._oid(teacher_id)
        class_oid = self._oid(class_id)
        subject_oid = self._oid(subject_id)
        actor_oid = self._oid(actor_id) if actor_id else None

        if self.class_repo.find_by_id(class_oid) is None:
            raise ClassNotFoundException(class_id)
        if self.subject_repo.find_by_id(subject_oid) is None:
            raise SubjectNotFoundException(subject_id)

        self.teacher_assignment_repo.assign(
            teacher_id=teacher_oid,
            class_id=class_oid,
            subject_id=subject_oid,
            actor_id=actor_oid,
        )
        return True