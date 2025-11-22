from __future__ import annotations
from typing import Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection


class TeacherReadModel:
    """
    Read model for teacher-related queries used by ClassFactory:
    - How many classes is this teacher currently assigned to?
    - What is their max class load?
    """

    def __init__(self, db: Database):
        # You may need to adjust these collection names
        self.classes: Collection = db["classes"]
        self.teachers: Collection = db["teachers"]

    def count_classes_for_teacher(self, teacher_id: ObjectId) -> int:
        """
        Count non-deleted classes where this teacher is the assigned teacher.
        """
        return self.classes.count_documents(
            {
                "teacher_id": teacher_id,
                "deleted": {"$ne": True},
            }
        )

    def get_max_class_load(self, teacher_id: ObjectId) -> Optional[int]:
        """
        Return the teacher's max class load if stored,
        or None if no limit is configured.
        """
        doc = self.teachers.find_one({"_id": teacher_id})
        if not doc:
            return None

        # Adjust field name if you use something different
        return doc.get("max_class_load")