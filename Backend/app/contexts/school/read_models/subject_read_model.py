# app/contexts/school/read_models/subject_read_model.py

from __future__ import annotations
from typing import Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection


class SubjectReadModel:
    """
    Read-only access for subject documents.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["subjects"]

    def get_by_id(self, subject_id: ObjectId) -> Optional[dict]:
        return self.collection.find_one(
            {"_id": subject_id, "is_deleted": {"$ne": True}}
        )

    def get_by_code(self, code: str) -> Optional[dict]:
        """
        SubjectFactory uses this for uniqueness checks.
        Expect codes to be stored upper-cased.
        """
        return self.collection.find_one(
            {"code": code.upper(), "is_deleted": {"$ne": True}}
        )

    def get_by_name(self, name: str) -> Optional[dict]:
        return self.collection.find_one(
            {"name": name, "is_deleted": {"$ne": True}}
        )