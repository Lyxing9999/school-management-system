from pymongo import ReturnDocument
from pymongo.database import Database
from bson import ObjectId
from typing import Any, Dict
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin


class StudentRepository(MongoErrorMixin):
    def __init__(self, db: Database, student_collection_name: str = "students"):
        self.db = db
        self.student_collection = self.db[student_collection_name]

    def save_student_info(self, user_id: ObjectId, student_info: dict) -> Dict[str, Any] | None:
        """
        Upsert student info:
        - If user exists: update student_info
        - If not exists: create new document
        """
        try:
            result = self.student_collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": {"student_info": student_info}},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            return result
        except Exception as e:
            self._handle_mongo_error("save_student_info", e)
            return None

    def get_student_info(self, user_id: ObjectId) -> Dict[str, Any] | None:
        """
        Fetch student info by user_id
        """
        try:
            return self.student_collection.find_one({"user_id": user_id})
        except Exception as e:
            self._handle_mongo_error("get_student_info", e)
            return None

    def update_student_info(self, user_id: ObjectId, student_info: dict) -> Dict[str, Any] | None:
        """
        Update existing student info; does not create if missing
        """
        try:
            result = self.student_collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": {"student_info": student_info}},
                return_document=ReturnDocument.AFTER
            )
            return result
        except Exception as e:
            self._handle_mongo_error("update_student_info", e)
            return None