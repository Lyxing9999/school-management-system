from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

LIFECYCLE_NOT_DELETED = {"lifecycle.deleted_at": None}

class TeacherAssignmentReadModel:
    """
    Checks if a teacher can grade a subject for a class.
    Backed by teacher_subject_assignments collection.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["teacher_subject_assignments"]

    def can_teacher_grade(
        self,
        *,
        teacher_id: ObjectId,
        class_id: ObjectId,
        subject_id: ObjectId,
    ) -> bool:
        doc = self.collection.find_one(
            {
                "teacher_id": teacher_id,
                "class_id": class_id,
                "subject_id": subject_id,
                **LIFECYCLE_NOT_DELETED,
            },
            {"_id": 1},
        )
        return doc is not None