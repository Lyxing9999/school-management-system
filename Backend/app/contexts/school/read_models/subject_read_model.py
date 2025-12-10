from __future__ import annotations

from typing import Optional, List, Dict, Any, Union, Iterable
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.error import MongoErrorMixin


class SubjectReadModel(MongoErrorMixin):
    """
    Read-only access for subject documents.

    Returned objects are plain dicts (Mongo docs), not domain aggregates.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["subjects"]

    # ------------ internal helpers ------------

    def _normalize_id(self, id_: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    # ------------ single-subject getters ------------

    def get_by_id(self, subject_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        oid = self._normalize_id(subject_id)
        try:
            return self.collection.find_one(
                {"_id": oid, "is_deleted": {"$ne": True}}
            )
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)
            return None

    def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        try:
            return self.collection.find_one(
                {"code": code.upper(), "is_deleted": {"$ne": True}}
            )
        except Exception as e:
            self._handle_mongo_error("get_by_code", e)
            return None

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        try:
            return self.collection.find_one(
                {"name": name, "is_deleted": {"$ne": True}}
            )
        except Exception as e:
            self._handle_mongo_error("get_by_name", e)
            return None

    def get_name_by_id(self, subject_id: Union[str, ObjectId]) -> Optional[str]:
        oid = self._normalize_id(subject_id)
        try:
            doc = self.collection.find_one(
                {"_id": oid, "is_deleted": {"$ne": True}},
                {"name": 1},
            )
            if not doc:
                return None
            return doc.get("name")
        except Exception as e:
            self._handle_mongo_error("get_name_by_id", e)
            return None

    def get_code_by_id(self, subject_id: Union[str, ObjectId]) -> Optional[str]:
        oid = self._normalize_id(subject_id)
        try:
            doc = self.collection.find_one(
                {"_id": oid, "is_deleted": {"$ne": True}},
                {"code": 1},
            )
            if not doc:
                return None
            return doc.get("code")
        except Exception as e:
            self._handle_mongo_error("get_code_by_id", e)
            return None

    # ------------ list / batch APIs ------------

    def list_all(self) -> List[Dict[str, Any]]:
        try:
            return list(self.collection.find({"is_deleted": {"$ne": True}}))
        except Exception as e:
            self._handle_mongo_error("list_all", e)
            return []

    def list_by_ids(
        self,
        subject_ids: List[Union[str, ObjectId]],
    ) -> List[Dict[str, Any]]:
        if not subject_ids:
            return []
        normalized_ids = [self._normalize_id(sid) for sid in subject_ids]
        try:
            return list(
                self.collection.find(
                    {
                        "_id": {"$in": normalized_ids},
                        "is_deleted": {"$ne": True},
                        "is_active": True,
                    }
                )
            )
        except Exception as e:
            self._handle_mongo_error("list_by_ids", e)
            return []

    def list_names_by_ids(
        self,
        subject_ids: Iterable[Union[str, ObjectId]],
    ) -> Dict[ObjectId, str]:
        """
        { subject_id -> name }
        """
        normalized_ids = [self._normalize_id(sid) for sid in subject_ids]
        if not normalized_ids:
            return {}
        try:
            cursor = self.collection.find(
                {
                    "_id": {"$in": normalized_ids},
                    "is_deleted": {"$ne": True},
                    "is_active": True,
                },
                {"_id": 1, "name": 1},
            )
            result: Dict[ObjectId, str] = {}
            for doc in cursor:
                _id = doc.get("_id")
                name = doc.get("name") or ""
                if _id is not None:
                    result[_id] = name
            return result
        except Exception as e:
            self._handle_mongo_error("list_names_by_ids", e)
            return {}

    def list_codes_by_ids(
        self,
        subject_ids: Iterable[Union[str, ObjectId]],
    ) -> Dict[ObjectId, str]:
        """
        { subject_id -> code }
        """
        normalized_ids = [self._normalize_id(sid) for sid in subject_ids]
        if not normalized_ids:
            return {}
        try:
            cursor = self.collection.find(
                {
                    "_id": {"$in": normalized_ids},
                    "is_deleted": {"$ne": True},
                    "is_active": True,
                },
                {"_id": 1, "code": 1},
            )
            result: Dict[ObjectId, str] = {}
            for doc in cursor:
                _id = doc.get("_id")
                code = doc.get("code") or ""
                if _id is not None:
                    result[_id] = code
            return result
        except Exception as e:
            self._handle_mongo_error("list_codes_by_ids", e)
            return {}

    def list_subject_for_class(
        self,
        class_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        """
        List subjects for a given class_id.

        NOTE: This assumes your `subjects` collection actually has a `class_id` field.
        If the relationship lives only in `classes.subject_ids`, you do not need this
        and should instead resolve via ClassReadModel + list_by_ids.
        """
        oid = self._normalize_id(class_id)
        try:
            cursor = self.collection.find(
                {
                    "class_id": oid,
                    "is_deleted": {"$ne": True},
                    "is_active": True,
                }
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_subject_for_class", e)
            return []

    def count_active_subjects(self) -> int:
        """
        Return the count of active subjects.
        """
        try:
            return self.collection.count_documents(
                {"is_deleted": {"$ne": True}, "is_active": True}
            )
        except Exception as e:
            self._handle_mongo_error("count_active_subjects", e)
            return 0
    
    def list_all_name_select(self) -> List[Dict[str, Any]]:
        try:
            cursor = self.collection.find(
                {
                    "is_deleted": {"$ne": True},
                    "is_active": True,
                }
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_all_name_select", e)
            return []