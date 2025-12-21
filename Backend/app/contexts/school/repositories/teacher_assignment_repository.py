from __future__ import annotations
from bson import ObjectId
from pymongo.collection import Collection
from app.contexts.shared.lifecycle.domain import now_utc

NOT_DELETED = {"lifecycle.deleted_at": None}
DELETED = {"lifecycle.deleted_at": {"$ne": None}}

class TeacherAssignmentRepository:
    def __init__(self, collection: Collection):
        self.collection = collection
        # Uniqueness among ALL rows is OK, but often better: unique among ACTIVE only (see note below)
        self.collection.create_index(
            [("teacher_id", 1), ("class_id", 1), ("subject_id", 1)],
            unique=True,
            background=True,
        )

    def assign(self, *, teacher_id: ObjectId, class_id: ObjectId, subject_id: ObjectId, actor_id: ObjectId | None = None) -> None:
        n = now_utc()

        # 1) Restore if soft-deleted
        restored = self.collection.update_one(
            {"teacher_id": teacher_id, "class_id": class_id, "subject_id": subject_id, **DELETED},
            {"$set": {
                "lifecycle.deleted_at": None,
                "lifecycle.deleted_by": None,
                "lifecycle.updated_at": n,
            }},
        )
        if restored.matched_count:
            return

        # 2) Touch if already active
        touched = self.collection.update_one(
            {"teacher_id": teacher_id, "class_id": class_id, "subject_id": subject_id, **NOT_DELETED},
            {"$set": {"lifecycle.updated_at": n}},
        )
        if touched.matched_count:
            return

        # 3) Insert new
        self.collection.insert_one({
            "_id": ObjectId(),
            "teacher_id": teacher_id,
            "class_id": class_id,
            "subject_id": subject_id,
            "lifecycle": {
                "created_at": n,
                "updated_at": n,
                "deleted_at": None,
                "deleted_by": None,
            },
        })

    def unassign(self, *, teacher_id: ObjectId, class_id: ObjectId, subject_id: ObjectId, actor_id: ObjectId) -> int:
        n = now_utc()
        res = self.collection.update_one(
            {"teacher_id": teacher_id, "class_id": class_id, "subject_id": subject_id, **NOT_DELETED},
            {"$set": {
                "lifecycle.deleted_at": n,
                "lifecycle.deleted_by": actor_id,
                "lifecycle.updated_at": n,
            }},
        )
        return res.modified_count