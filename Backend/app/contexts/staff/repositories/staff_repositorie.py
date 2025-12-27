from __future__ import annotations

from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo import ASCENDING
from app.contexts.core.error import MongoErrorMixin
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.decorators.mongo_wrappers import mongo_operation

from app.contexts.shared.lifecycle.filters import (
    not_deleted,
    guard_not_deleted,
    guard_deleted,
)
from app.contexts.shared.lifecycle.types import (
    apply_soft_delete_update,
    apply_restore_update,
    now_utc,
)

from app.contexts.staff.mapper.staff_mapper import StaffMapper
from app.contexts.staff.domain.staff import Staff


class MongoStaffRepository(MongoErrorMixin):
    def __init__(self, collection: Collection):
        self.collection = collection
        self._mapper = StaffMapper  # OK only if StaffMapper methods are @staticmethod

    def _oid(self, value: ObjectId | str) -> ObjectId:
        return mongo_converter.convert_to_object_id(value)
    
    @mongo_operation("find_one")
    def find_one(self, staff_id: ObjectId | str, include_deleted: bool = False) -> Optional[Staff]:
        oid = self._oid(staff_id)
        q = {"_id": oid} if include_deleted else not_deleted({"_id": oid})

        doc = self.collection.find_one(q)
        return self._mapper.to_domain(doc) if doc else None

    @mongo_operation("insert")
    def save(self, staff: Staff) -> ObjectId:
        doc = self._mapper.to_persistence_dict(staff)
        return self.collection.insert_one(doc).inserted_id

    @mongo_operation("update")
    def update(self, staff_id: ObjectId | str, patch: dict) -> int:
        if not patch:
            return 0

        oid = self._oid(staff_id)

        # prevent lifecycle injection from outside
        patch.pop("lifecycle", None)

        res = self.collection.update_one(
            guard_not_deleted(oid),
            {"$set": {**patch, "lifecycle.updated_at": now_utc()}},
        )
        return res.modified_count

    @mongo_operation("soft_delete")
    def soft_delete(self, staff_id: ObjectId | str, deleted_by: ObjectId) -> int:
        oid = self._oid(staff_id)
        res = self.collection.update_one(
            guard_not_deleted(oid),
            apply_soft_delete_update(deleted_by),
        )
        return res.modified_count

    @mongo_operation("restore")
    def restore(self, staff_id: ObjectId | str) -> int:
        oid = self._oid(staff_id)
        # restore should target a deleted doc, not guard_not_deleted
        res = self.collection.update_one(
            guard_deleted(oid),
            apply_restore_update(),
        )
        return res.modified_count

    @mongo_operation("delete")
    def delete(self, staff_id: ObjectId | str) -> int:
        oid = self._oid(staff_id)
        res = self.collection.delete_one({"_id": oid})
        return res.deleted_count