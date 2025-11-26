from __future__ import annotations
from typing import Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection


class GradeReadModel:
    """
    Read-only access for grade documents.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["grades"]

    def list_class_grades(self, class_id: ObjectId) -> list[dict]:
        return list(self.collection.find({"class_id": class_id}))
    
    def list_student_grades(self, student_id: ObjectId) -> list[dict]:
        return list(self.collection.find({"student_id": student_id}))