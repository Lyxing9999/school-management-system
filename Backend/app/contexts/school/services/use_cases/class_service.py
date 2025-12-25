from __future__ import annotations

from typing import Iterable
from bson import ObjectId

from app.contexts.school.domain.class_section import ClassSection, ClassSectionStatus
from app.contexts.school.errors.class_exceptions import ClassNotFoundException

from ._base import OidMixin


class ClassService(OidMixin):
    def __init__(self, *, class_repo, class_factory, class_lifecycle):
        self.class_repo = class_repo
        self.class_factory = class_factory
        self.class_lifecycle = class_lifecycle

    # ------------------------
    # Create / Read
    # ------------------------

    def create_class(
        self,
        name: str,
        teacher_id: str | ObjectId | None = None,
        subject_ids: Iterable[str | ObjectId] | None = None,
        max_students: int | None = None,
    ) -> ClassSection:
        section = self.class_factory.create_class(
            name=name,
            teacher_id=teacher_id,
            subject_ids=subject_ids,
            max_students=max_students,
        )
        return self.class_repo.insert(section)

    def get_class_by_id(self, class_id: str | ObjectId) -> ClassSection | None:
        return self.class_repo.find_by_id(self._oid(class_id))

    # ------------------------
    # Domain behaviors
    # ------------------------

    def assign_teacher_to_class(self, class_id: str | ObjectId, teacher_id: str | ObjectId) -> ClassSection:
        class_oid = self._oid(class_id)
        teacher_oid = self._oid(teacher_id)

        section = self.class_repo.find_by_id(class_oid)
        if section is None:
            raise ClassNotFoundException(str(class_id))

        section.assign_teacher(teacher_oid)

        updated = self.class_repo.update(section)
        if updated is None:
            raise ClassNotFoundException(str(class_id))
        return section

    def set_class_status(self, class_id: str | ObjectId, status: ClassSectionStatus | str) -> ClassSection:
        class_oid = self._oid(class_id)

        section = self.class_repo.find_by_id(class_oid)
        if section is None:
            raise ClassNotFoundException(str(class_id))

        # domain decides validity
        section.set_status(status)

        updated = self.class_repo.update(section)
        if updated is None:
            raise ClassNotFoundException(str(class_id))
        return updated

    # ------------------------
    # Lifecycle operations
    # ------------------------

    def soft_delete_class(self, class_id: str | ObjectId, actor_id: str | ObjectId) -> bool:
        oid = self._oid(class_id)
        actor_oid = self._oid(actor_id)
        res = self.class_lifecycle.soft_delete_class(oid, actor_oid)
        return res.modified_count > 0

    def restore_class(self, class_id: str | ObjectId, actor_id: str | ObjectId) -> bool:
        oid = self._oid(class_id)
        actor_oid = self._oid(actor_id)
        res = self.class_lifecycle.restore_class(oid, actor_oid)
        return res.modified_count > 0

    def hard_delete_class(self, class_id: str | ObjectId, actor_id: str | ObjectId) -> bool:
        oid = self._oid(class_id)
        actor_oid = self._oid(actor_id)
        res = self.class_lifecycle.hard_delete_class(oid, actor_oid)
        return res.deleted_count > 0