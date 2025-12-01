from typing import Iterable, List, Dict

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.error import MongoErrorMixin


class ScheduleReadModel(MongoErrorMixin):
    """
    Read-only access for schedule documents.

    Returned objects are plain dicts (Mongo docs), not domain aggregates.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["schedule"]

    # ------------ internal helpers ------------

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        """
        Convert incoming id to ObjectId using shared converter.
        """
        return mongo_converter.convert_to_object_id(id_)

    # ------------ public API ------------
    def get_by_id(self, id_: ObjectId | str) -> Dict:
        """
        Return a non-deleted schedule document by id.
        """
        oid = self._normalize_id(id_)
        try:
            cursor = self.collection.find_one({"_id": oid, "deleted": {"$ne": True}})
            return cursor
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)
            return None
    def list_all(self) -> List[Dict]:
        """
        Return all non-deleted schedule documents.
        """
        try:
            cursor = self.collection.find({"deleted": {"$ne": True}})
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_all", e)
            return []

    def list_student_schedules(self, student_id: ObjectId | str) -> List[Dict]:
        """
        Return all non-deleted schedule documents for a given student_id.
        """
        oid = self._normalize_id(student_id)
        try:
            cursor = self.collection.find(
                {
                    "student_id": oid,
                    "deleted": {"$ne": True},
                }
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_student_schedules", e)
            return []

    def list_class_schedules(self, class_id: ObjectId | str) -> List[Dict]:
        """
        Return all non-deleted schedule documents for a given class_id.
        """
        oid = self._normalize_id(class_id)
        try:
            cursor = self.collection.find(
                {
                    "class_id": oid,
                    "deleted": {"$ne": True},
                }
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_class_schedules", e)
            return []

    def list_classes_schedules(
        self,
        class_ids: Iterable[str | ObjectId],
    ) -> List[Dict]:
        """
        Return all non-deleted schedule documents for multiple class_ids.
        """
        normalized_ids: List[ObjectId] = [
            self._normalize_id(cid) for cid in class_ids
        ]
        if not normalized_ids:
            return []
        try:
            cursor = self.collection.find(
                {
                    "class_id": {"$in": normalized_ids},
                    "deleted": {"$ne": True},
                }
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_classes_schedules", e)
            return []

    def list_teacher_schedules(self, teacher_id: ObjectId | str) -> List[Dict]:
        """
        Return all non-deleted schedule documents for a given teacher_id.
        """
        oid = self._normalize_id(teacher_id)
        try:
            cursor = self.collection.find(
                {
                    "teacher_id": oid,
                    "deleted": {"$ne": True},
                }
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_teacher_schedules", e)
            return []

    def list_subject_schedules(self, subject_id: ObjectId | str) -> List[Dict]:
        """
        Return all non-deleted schedule documents for a given subject_id.
        """
        oid = self._normalize_id(subject_id)
        try:
            cursor = self.collection.find(
                {
                    "subject_id": oid,
                    "deleted": {"$ne": True},
                }
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_subject_schedules", e)
            return []