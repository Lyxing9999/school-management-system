from __future__ import annotations
from typing import Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from app.contexts.shared.model_converter import mongo_converter

class GradeReadModel:
    """
    Read-only access for grade documents.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["grades"]
    
    def list_class_grades(self, class_id: ObjectId | str) -> list[dict]:
        oid = mongo_converter.convert_to_object_id(class_id)
        return list(self.collection.find({"class_id": oid}))
    
    def list_student_grades(self, student_id: ObjectId) -> list[dict]:
        oid = mongo_converter.convert_to_object_id(student_id)
        return list(self.collection.find({"student_id": student_id}))

    