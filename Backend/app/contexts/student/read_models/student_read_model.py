from typing import List, Dict, Any, Optional, Iterable 
from bson import ObjectId
from pymongo.database import Database
from pymongo.cursor import Cursor
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.student.filters.student_filters import active as student_active
from app.contexts.student.filters.student_filters import not_deleted as student_not_deleted

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



    def find_active_students_by_ids(self, student_ids: List[ObjectId]) -> Cursor:
        query = {"$and": [student_active(), {"_id": {"$in": student_ids}}]}
        return self.collection.find(query)

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


    def list_student_name_options(
        self,
        filter: Dict[str, Any] = None,
        projection: Optional[Dict[str, int]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        filter = filter or {}

        proj = projection or {
            "_id": 1,
            "first_name_en": 1,
            "last_name_en": 1,
            "first_name_kh": 1,
            "last_name_kh": 1,
        }

        cursor = self.collection.find(filter, proj)

        if limit is not None:
            cursor = cursor.limit(int(limit))

        return list(cursor)


    def count_active_students(self) -> int:
        return self.collection.count_documents(student_active())

        
    def list_student_ids_in_class(self, class_id: ObjectId, *, session=None) -> set[ObjectId]:
        cur = self.collection.find(
            {"current_class_id": class_id, "lifecycle.deleted_at": None},
            {"_id": 1},
            session=session,
        )
        return {d["_id"] for d in cur}

    def exists(self, student_id: ObjectId, *, session=None) -> bool:
        return self.collection.count_documents({"_id": student_id, "lifecycle.deleted_at": None}, limit=1, session=session) == 1


    def get_current_class_id(self, student_id: ObjectId, *, session=None) -> Optional[ObjectId]:
        doc = self.collection.find_one({"_id": student_id}, {"current_class_id": 1}, session=session)
        return doc.get("current_class_id") if doc else None