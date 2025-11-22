from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection


class ScheduleReadModel:
    """
    Read-only access for schedule documents.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["schedules"]

    # Add methods for schedule-related read operations here
    def list_for_student(self, student_id: ObjectId) -> list[dict]:
        return list(self.collection.find({"student_id": student_id}))
        
    def list_for_class(self, class_id: ObjectId) -> list[dict]:
        return list(self.collection.find({"class_id": class_id}))
        
    def list_for_teacher(self, teacher_id: ObjectId) -> list[dict]:
        return list(self.collection.find({"teacher_id": teacher_id}))
        