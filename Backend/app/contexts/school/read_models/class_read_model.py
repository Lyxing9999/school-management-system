from __future__ import annotations
from typing import Optional, List, Dict

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from app.contexts.shared.model_converter import mongo_converter


class ClassReadModel:
    """
    Read-side helper for ClassSection data.

    Returned objects are plain dicts (Mongo docs), not domain aggregates.
    Used by factories and query/use-case code that only needs to *read*.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["classes"]

    # ------------ internal helpers ------------

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        """
        Convert incoming id to ObjectId using shared converter.
        """
        return mongo_converter.convert_to_object_id(id_)

    # ------------ public API ------------

    def get_by_id(self, id_: str | ObjectId) -> Optional[Dict]:
        """
        Fetch class document by _id (ignores soft-deleted records).
        Returns Mongo document (dict) or None.
        """
        oid = self._normalize_id(id_)
        doc = self.collection.find_one(
            {"_id": oid, "deleted": {"$ne": True}}
        )
        return doc

    def get_by_name(self, name: str) -> Optional[Dict]:
        """
        Fetch class document by name (ignores soft-deleted records).
        Used by ClassFactory to enforce unique class names.
        """
        doc = self.collection.find_one(
            {"name": name, "deleted": {"$ne": True}}
        )
        return doc

    def list_all(self) -> List[Dict]:
        """
        Return all non-deleted class documents as plain dicts.
        """
        cursor = self.collection.find({"deleted": {"$ne": True}})
        return [doc for doc in cursor]


    def list_teacher_classes(self, teacher_id: str | ObjectId) -> List[Dict]:
        """
        Return all non-deleted class documents where the given teacher is assigned.
        """
        oid = self._normalize_id(teacher_id)
        return list(self.collection.find({
            "teacher_id": oid,
            "deleted": {"$ne": True}
        }))
        
    def list_student_classes(self, student_id: str | ObjectId) -> List[Dict]:
        """
        Return all non-deleted class documents where the given student is enrolled.
        """
        oid = self._normalize_id(student_id)
        return list(self.collection.find({
            "student_ids": oid,
            "deleted": {"$ne": True}
        }))
    
    def list_students_in_class(self, class_id: str | ObjectId) -> List[Dict]:
        """
        Return all non-deleted student documents enrolled in the given class.
        """
        oid = self._normalize_id(class_id)
        return list(self.collection.find_one({
            "_id" : oid,
            "deleted": {"$ne": True}
        })['student_ids'])

