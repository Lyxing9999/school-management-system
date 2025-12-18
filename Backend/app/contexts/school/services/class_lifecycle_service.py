from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from contexts.shared.lifecycle.types import active_filter, now_utc


class ClassLifecycleService:
    def __init__(self, db: Database):
        self.db = db
        self.classes = db.classes
        self.students = db.students

    def recompute_enrolled_count(self, class_id: ObjectId) -> int:
        count = self.students.count_documents(active_filter({"current_class_id": class_id}))
        self.classes.update_one(
            {"_id": class_id},
            {"$set": {"enrolled_count": count, "updated_at": now_utc()}}
        )
        return count