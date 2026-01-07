from __future__ import annotations

from typing import Iterable, Optional
from bson import ObjectId

from app.contexts.school.domain.subject import Subject
from app.contexts.school.errors.subject_exceptions import SubjectNotFoundException, InvalidSubjectCodeError

from ._base import OidMixin


class SubjectService(OidMixin):
    def __init__(self, *, subject_repo, subject_factory, subject_lifecycle, subject_update_policy):
        self.subject_repo = subject_repo
        self.subject_factory = subject_factory
        self.subject_lifecycle = subject_lifecycle
        self.subject_update_policy = subject_update_policy
    # ------------------------
    # Create / Read
    # ------------------------

    def create_subject(
        self,
        name: str,
        code: str,
        description: str | None = None,
        allowed_grade_levels: Iterable[int] | None = None,
    ) -> Subject:
        subject = self.subject_factory.create_subject(
            name=name,
            code=code,
            description=description,
            allowed_grade_levels=allowed_grade_levels,
        )
        return self.subject_repo.insert(subject)

    def get_subject_by_id(self, subject_id: str | ObjectId) -> Subject | None:
        return self.subject_repo.find_by_id(self._oid(subject_id))

    def get_subject_by_code(self, code: str) -> Subject | None:
        return self.subject_repo.find_by_code(code)

    # ------------------------
    # Domain status toggles
    # ------------------------

    def deactivate_subject(self, subject_id: str | ObjectId) -> Subject:
        oid = self._oid(subject_id)
        subject = self.subject_repo.find_by_id(oid)
        if subject is None:
            raise SubjectNotFoundException(str(subject_id))

        subject.deactivate()
        updated = self.subject_repo.update(subject)
        if updated is None:
            raise SubjectNotFoundException(str(subject_id))
        return updated

    def activate_subject(self, subject_id: str | ObjectId) -> Subject:
        oid = self._oid(subject_id)
        subject = self.subject_repo.find_by_id(oid)
        if subject is None:
            raise SubjectNotFoundException(str(subject_id))

        subject.activate()
        updated = self.subject_repo.update(subject)
        if updated is None:
            raise SubjectNotFoundException(str(subject_id))
        return updated
    def update_subject_patch(
        self,
        subject_id: str | ObjectId,
        *,
        name: str | None = None,
        code: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> Subject:
        oid = self._oid(subject_id)
        subject = self.subject_repo.find_by_id(oid)
        if subject is None:
            raise SubjectNotFoundException(str(subject_id))

        final_code = (code.strip().upper() if code is not None else subject.code)
        final_name = (name.strip() if name is not None else subject.name)

        # check uniqueness only for fields user is trying to change (optional)
        self.subject_update_policy.ensure_unique(
            subject_id=subject.id,
            code=final_code if code is not None else None,
            name=final_name if name is not None else None,
        )

        subject.apply_patch(
            name=name,
            code=final_code,
            description=description,
            is_active=is_active,
        )

        updated = self.subject_repo.update(subject)
        if updated is None:
            raise SubjectNotFoundException(str(subject_id))
        return updated
    # ------------------------
    # Lifecycle operations (soft delete / restore / hard delete)
    # ------------------------

    def soft_delete_subject(self, subject_id: str | ObjectId, actor_id: str | ObjectId) -> bool:
        oid = self._oid(subject_id)
        actor_oid = self._oid(actor_id)

        res = self.subject_lifecycle.soft_delete_subject(oid, actor_oid)
        return res.modified_count > 0

    def restore_subject(self, subject_id: str | ObjectId) -> bool:
        oid = self._oid(subject_id)

        res = self.subject_lifecycle.restore_subject(oid)
        return res.modified_count > 0

    def hard_delete_subject(self, subject_id: str | ObjectId, actor_id: str | ObjectId) -> bool:
        oid = self._oid(subject_id)
        actor_oid = self._oid(actor_id)

        res = self.subject_lifecycle.hard_delete_subject(oid, actor_oid)
        return res.deleted_count > 0