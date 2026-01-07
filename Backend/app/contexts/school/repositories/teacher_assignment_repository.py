
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.lifecycle.filters import not_deleted, by_show_deleted, ShowDeleted
from app.contexts.school.domain.teaching_assignment import TeachingAssignmentRecord
from app.contexts.school.mapper.teaching_assignment_mapper import TeachingAssignmentMapper


class TeacherAssignmentRepository:
    def __init__(self, db: Database):
        self.col: Collection = db["teacher_subject_assignments"]

    def insert(self, rec: TeachingAssignmentRecord) -> TeachingAssignmentRecord:
        self.col.insert_one(TeachingAssignmentMapper.to_persistence(rec))
        return rec

    def find_by_id(self, assignment_id: ObjectId, *, show_deleted: ShowDeleted = "active") -> Optional[TeachingAssignmentRecord]:
        q = by_show_deleted(show_deleted, {"_id": assignment_id})
        doc = self.col.find_one(q)
        return TeachingAssignmentMapper.to_domain(doc) if doc else None

    def update(self, rec: TeachingAssignmentRecord) -> TeachingAssignmentRecord:
        self.col.replace_one({"_id": rec.id}, TeachingAssignmentMapper.to_persistence(rec))
        return rec

    def soft_delete_by_id(self, assignment_id: ObjectId, actor_id: ObjectId) -> int:
        res = self.col.update_one(
            not_deleted({"_id": assignment_id}),
            {
                "$set": {
                    "lifecycle.deleted_at": datetime.utcnow(),
                    "lifecycle.deleted_by": actor_id,
                }
            },
        )
        return int(res.modified_count)

    def soft_delete_by_class_subject(self, *, class_id: ObjectId, subject_id: ObjectId, actor_id: ObjectId) -> int:
        res = self.col.update_one(
            not_deleted({"class_id": class_id, "subject_id": subject_id}),
            {
                "$set": {
                    "lifecycle.deleted_at": datetime.utcnow(),
                    "lifecycle.deleted_by": actor_id,
                }
            },
        )
        return int(res.modified_count)

    