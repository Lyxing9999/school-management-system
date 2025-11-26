from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from app.contexts.shared.model_converter import mongo_converter

class ScheduleReadModel:
    """
    Read-only access for schedule documents.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["schedule"]

    def list_all_schedules(self) -> list[dict]:
        return list(self.collection.find())

    def list_student_schedules(self, student_id: ObjectId) -> list[dict]:
        oid = mongo_converter.convert_to_object_id(student_id)
        return list(self.collection.find({
            "student_id": oid,
        }))
    
    def list_class_schedules(self, class_id: ObjectId) -> list[dict]:
        oid = mongo_converter.convert_to_object_id(class_id)
        return list(self.collection.find({
            "class_id": oid,
        }))
        
    def list_teacher_schedules(self, teacher_id: ObjectId) -> list[dict]:
        oid = mongo_converter.convert_to_object_id(teacher_id)
        return list(self.collection.find({
            "teacher_id": oid,
        }))

    def list_subject_schedules(self, subject_id: ObjectId) -> list[dict]:
        oid = mongo_converter.convert_to_object_id(subject_id)
        return list(self.collection.find({
            "subject_id": oid,
        }))
        