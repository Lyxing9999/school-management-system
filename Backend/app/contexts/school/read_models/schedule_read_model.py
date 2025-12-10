from typing import Iterable, List, Dict, Union, Any

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.error import MongoErrorMixin
import datetime as dt


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

    # ------------ basic read API ------------

    def get_by_id(self, id_: ObjectId | str) -> Dict | None:
        """
        Return a non-deleted schedule document by id.
        """
        oid = self._normalize_id(id_)
        try:
            doc = self.collection.find_one({"_id": oid, "deleted": {"$ne": True}})
            return doc
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


    
    def list_schedules_for_class(self, class_id: ObjectId | str) -> List[Dict]:
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
            self._handle_mongo_error("list_schedules_for_class", e)
            return []

    def list_schedules_for_classes(
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
            self._handle_mongo_error("list_schedules_for_classes", e)
            return []

    def list_schedules_for_teacher(self, teacher_id: ObjectId | str) -> List[Dict]:
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
            self._handle_mongo_error("list_schedules_for_teacher", e)
            return []

    def list_schedules_for_subject(self, subject_id: ObjectId | str) -> List[Dict]:
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
            self._handle_mongo_error("list_schedules_for_subject", e)
            return []

    def count_lessons_for_date(self, date: dt.date) -> int:
        """
        Count how many lessons are scheduled on a given calendar date.

        Since schedule docs use `day_of_week` (1=Mon..7=Sun), we:
        - convert the given date to its ISO weekday
        - count non-deleted schedule documents for that weekday
        """
        # dt.date.isoweekday(): Monday=1 ... Sunday=7
        weekday = date.isoweekday()

        query = {
            "day_of_week": weekday,
            "deleted": {"$ne": True},
        }

        try:
            return self.collection.count_documents(query)
        except Exception as e:
            self._handle_mongo_error("count_lessons_for_date", e)
            return 0

    # ------------ relationship helpers ------------

    def has_schedules_for_teacher(self, teacher_id: Union[ObjectId, str]) -> bool:
        """
        Return True if the teacher has at least one (non-deleted) schedule,
        False otherwise.
        """
        oid = self._normalize_id(teacher_id)

        query = {
            "teacher_id": oid,
            "deleted": {"$ne": True},
        }

        try:
            return self.collection.find_one(query) is not None
        except Exception as e:
            self._handle_mongo_error("has_schedules_for_teacher", e)
            raise

    def count_schedules_for_teacher(self, teacher_id: Union[ObjectId, str]) -> int:
        """
        Return the number of non-deleted schedules for this teacher.
        """
        oid = self._normalize_id(teacher_id)

        query = {
            "teacher_id": oid,
            "deleted": {"$ne": True},
        }

        try:
            return self.collection.count_documents(query)
        except Exception as e:
            self._handle_mongo_error("count_schedules_for_teacher", e)
            raise

    # ------------ aggregation for admin dashboard ------------

    def aggregate_lessons_by_weekday(self) -> List[Dict[str, Any]]:
        """
        Admin dashboard: count how many lessons exist per day_of_week.

        Returns:
        [
          { "day_of_week": 1, "lesson_count": 5 },
          { "day_of_week": 2, "lesson_count": 8 },
          ...
        ]
        """
        pipeline = [
            {
                "$match": {
                    "deleted": {"$ne": True},
                }
            },
            {
                "$group": {
                    "_id": "$day_of_week",
                    "lesson_count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "day_of_week": "$_id",
                    "lesson_count": 1,
                }
            },
            {
                "$sort": {"day_of_week": 1}
            },
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_lessons_by_weekday", e)
            return []

    def aggregate_lessons_by_teacher(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Admin dashboard: count lessons per teacher (top N).

        Returns:
        [
          { "teacher_id": "69252fd678b90ceeb4b58081", "lesson_count": 24 },
          ...
        ]
        """
        if limit <= 0:
            limit = 10

        pipeline = [
            {
                "$match": {
                    "deleted": {"$ne": True},
                }
            },
            {
                "$group": {
                    "_id": "$teacher_id",
                    "lesson_count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "teacher_id": {"$toString": "$_id"},
                    "lesson_count": 1,
                }
            },
            {
                "$sort": {"lesson_count": -1}
            },
            {
                "$limit": limit
            },
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_lessons_by_teacher", e)
            return []