from __future__ import annotations
from typing import Optional, List, Dict, Any

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from app.contexts.shared.model_converter import mongo_converter


class ClassReadModel:
    """
    Read-side helper for Class data.

    Returned objects are plain dicts (Mongo docs), not domain aggregates.
    Used by factories and query/use-case code that only needs to read.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["classes"]

    # ------------ internal helpers ------------

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        """
        Convert incoming id to ObjectId using shared converter.
        """
        return mongo_converter.convert_to_object_id(id_)

    # ------------ public API: single fetches ------------

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

    def get_name_by_id(self, class_id: str | ObjectId) -> Optional[str]:
        """
        Return the name of the given class, or None if not found.
        """
        oid = self._normalize_id(class_id)
        doc = self.collection.find_one(
            {"_id": oid, "deleted": {"$ne": True}},
            {"name": 1},
        )
        if not doc:
            return None
        return doc.get("name")

    # ------------ public API: class lists ------------

    def list_all(self) -> List[Dict]:
        """
        Return all non-deleted class documents as plain dicts.
        """
        cursor = self.collection.find({"deleted": {"$ne": True}})
        return list(cursor)

    def list_classes_for_teacher(self, teacher_id: str | ObjectId) -> List[Dict]:
        """
        Return all non-deleted class documents where the given teacher is assigned.
        """
        oid = self._normalize_id(teacher_id)
        return list(
            self.collection.find(
                {
                    "teacher_id": oid,
                    "deleted": {"$ne": True},
                }
            )
        )

    def list_classes_for_student(self, student_id: str | ObjectId) -> List[Dict]:
        """
        Return all non-deleted class documents where the given student is enrolled.
        """
        oid = self._normalize_id(student_id)
        return list(self.collection.find({"student_ids": oid, "deleted": {"$ne": True}}))

    # ------------ public API: ID lists ------------

    def list_student_ids_for_class(self, class_id: str | ObjectId) -> List[ObjectId]:
        """
        Return the list of student_ids (ObjectId) enrolled in the given class.
        """
        oid = self._normalize_id(class_id)
        doc = self.collection.find_one(
            {"_id": oid, "deleted": {"$ne": True}},
            {"student_ids": 1},
        )
        if not doc:
            return []
        student_ids = doc.get("student_ids") or []
        return [self._normalize_id(sid) for sid in student_ids]

    def list_subject_ids_for_class(self, class_id: str | ObjectId) -> List[ObjectId]:
        """
        Return the list of subject_ids (ObjectId) in the given class.
        """
        oid = self._normalize_id(class_id)
        doc = self.collection.find_one(
            {"_id": oid, "deleted": {"$ne": True}},
            {"subject_ids": 1},
        )
        if not doc:
            return []
        subject_ids = doc.get("subject_ids") or []
        return [self._normalize_id(sid) for sid in subject_ids]

    # ------------ public API: names / projections ------------

    def list_class_names(self) -> List[Dict]:
        """
        Return all non-deleted classes with only the name field projected.
        Each dict will contain at least `_id` and `name`.
        """
        cursor = self.collection.find(
            {"deleted": {"$ne": True}},
            {"name": 1},
        )
        return list(cursor)

    def list_class_names_by_ids(self, class_ids: List[ObjectId]) -> Dict[ObjectId, str]:
        """
        Given a list of class_ids, return a mapping {class_id: name}.
        Only returns entries for classes that exist and are not deleted.
        """
        if not class_ids:
            return {}
        cursor = self.collection.find(
            {"_id": {"$in": class_ids}, "deleted": {"$ne": True}},
            {"_id": 1, "name": 1},
        )
        result: Dict[ObjectId, str] = {}
        for doc in cursor:
            cid = doc.get("_id")
            name = doc.get("name")
            if cid is not None and name is not None:
                result[cid] = name
        return result

    def list_class_name_options_for_teacher(
        self,
        teacher_id: str | ObjectId,
    ) -> List[Dict[str, Any]]:
        """
        Return class options for a teacher, shaped for UI select:

        [
          { "id": "ObjectIdString", "name": "Grade 7A" },
          ...
        ]
        """
        oid = self._normalize_id(teacher_id)
        docs = self.list_classes_for_teacher(oid)

        options: List[Dict[str, Any]] = []
        for c in docs:
            cid = c.get("_id")
            if not cid:
                continue
            options.append(
                {
                    "id": str(cid),
                    "name": c.get("name", ""),
                }
            )
        return options