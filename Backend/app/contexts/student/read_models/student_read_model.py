from __future__ import annotations
from typing import List, Dict, Any, Optional
from bson import ObjectId
from pydantic.v1.utils import Obj
from pymongo.database import Database
from pymongo.cursor import Cursor
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin

from app.contexts.shared.model_converter import mongo_converter


class StudentReadModel(MongoErrorMixin):
    """
    Read-side facade for student use cases.

    Responsibilities:
    - Expose low-level read models for IAM, class, schedule, etc.
    - Provide higher-level queries for "my classes", "my schedule", "my attendance"
      with ObjectIds normalized to strings and names attached for UI.
    """

    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db["students"]
        from app.contexts.iam.read_models.iam_read_model import IAMReadModel
        self._iam_read_model = IAMReadModel(db)



    # -------------
    # external helper methods
    # -------------


    def _normalize_ids(self, ids: Iterable[str | ObjectId | None]) -> list[ObjectId]:
        normalized: list[ObjectId] = []

        for raw_id in ids:
            if raw_id is None:
                continue

            # Skip empty/whitespace strings
            if isinstance(raw_id, str) and not raw_id.strip():
                continue

            normalized.append(mongo_converter.convert_to_object_id(raw_id))

        return normalized


    # -------------
    # basic
    # -------------
    def get_by_user_id(self, user_id: ObjectId):
            return self.collection.find_one({"user_id": user_id})
            
    def get_by_id(self, student_id: ObjectId):
            return self.collection.find_one({"_id": student_id})
    def get_me(self, user_id: ObjectId) -> dict | None:
        """
        Simple pass-through to IAM get_by_id.
        """
        return self.get_by_user_id(user_id)

    def get_by_student_code(self, code: str):
            return self.collection.find_one({"student_id_code": code})

    def list_students_by_current_class_ids(
        self,
        class_ids: List[str | ObjectId],
        *,
        projection: Optional[Dict[str, int]] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        print("get id from api ", class_ids)
        oids = self._normalize_ids(class_ids)
        if not oids:
            return []
        print("after normalize", oids)
        query: Dict[str, Any] = {"current_class_id": {"$in": oids}}

        if active_only:
            query["deleted"] = {"$ne": True}
            query["status"] = "Active"

        return list(self.collection.find(query))


    def list_students_by_current_class_id(
        self,
        class_id: str | ObjectId,
        *,
        projection: Optional[Dict[str, int]] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Convenience wrapper for a single class_id.
        Returns all students whose current_class_id == class_id.
        """


        student = self.list_students_by_current_class_ids(
            [class_id],
            active_only=active_only,
        )
        return student
    def list_student_ids_by_current_class_ids(self, class_ids: List[str | ObjectId], *, active_only: bool = True,) -> List[ObjectId]:
        docs = self.list_students_by_current_class_ids(class_ids, projection={"_id": 1}, active_only=active_only)
        return [d["_id"] for d in docs if d.get("_id")]


    def find_active_students_by_ids(self, student_ids: List[ObjectId]) -> Cursor:
        return self.collection.find(
            {
                "_id": {"$in": student_ids},
                "status": "active",
                "is_deleted": {"$ne": True}, 
            }
        )


    def list_student_names_by_ids(self, student_ids: list) -> List[Dict[str, Any]]:
        ids = self._normalize_ids(student_ids)
        cursor = self.collection.find(
            {"_id": {"$in": ids}},
            {"first_name_en": 1, "last_name_en": 1, "first_name_kh": 1, "last_name_kh": 1}
        )
        return list(cursor)


    # -------------
    # options select
    # -------------

    def list_student_name_options(self, filter: dict = {}) -> List[Dict[str, Any]]:
        cursor = self.collection.find(
            filter=filter,
            projection={
                "_id": 1,
                "first_name_en": 1,
                "last_name_en": 1,
                "first_name_kh": 1,
                "last_name_kh": 1,
            },
        )

        return cursor


    def count_active_students(self) -> int:
        """
        Return the count of active students.
        """
        return self._iam_read_model.count_active_users("student")