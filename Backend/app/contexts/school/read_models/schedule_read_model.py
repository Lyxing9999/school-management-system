import datetime as dt
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.core.errors import MongoErrorMixin
from app.contexts.shared.lifecycle.filters import not_deleted
from app.contexts.shared.model_converter import mongo_converter


class ScheduleReadModel(MongoErrorMixin):
    """
    Read-only access for schedule documents.

    Returned objects are plain dicts (Mongo docs), not domain aggregates.
    Applies lifecycle soft-delete filter via `not_deleted(...)`.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["schedules"]

    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def get_by_id(self, id_: ObjectId | str) -> Dict[str, Any] | None:
        oid = self._oid(id_)
        try:
            doc = self.collection.find_one(not_deleted({"_id": oid}))
            return doc
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)
            return None

    def list_all(self) -> List[Dict[str, Any]]:
        try:
            cursor = self.collection.find(not_deleted())
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_all", e)
            return []

    def list_schedules_for_class_paginated(
        self,
        class_id: ObjectId | str,
        page: int = 1,
        page_size: int = 10,
        sort: Optional[List[tuple[str, int]]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        oid = self._oid(class_id)

        page = max(1, int(page))
        page_size = min(max(1, int(page_size)), 100)
        skip = (page - 1) * page_size

        query = not_deleted({"class_id": oid})

        if sort is None:
            sort = [("day_of_week", 1), ("start_time", 1), ("_id", 1)]

        try:
            total = self.collection.count_documents(query)
            cursor = (
                self.collection.find(query)
                .sort(sort)
                .skip(skip)
                .limit(page_size)
            )
            return list(cursor), total
        except Exception as e:
            self._handle_mongo_error("list_schedules_for_class_paginated", e)
            return [], 0

    def list_schedules_for_classes(
        self,
        class_ids: Iterable[str | ObjectId],
    ) -> List[Dict[str, Any]]:
        normalized_ids: List[ObjectId] = [self._oid(cid) for cid in class_ids]
        if not normalized_ids:
            return []
        try:
            cursor = self.collection.find(
                not_deleted({"class_id": {"$in": normalized_ids}})
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_schedules_for_classes", e)
            return []
    @staticmethod
    def _is_hhmm(s: str) -> bool:
        if not s or len(s) != 5 or s[2] != ":":
            return False
        hh, mm = s[:2], s[3:]
        return (
            hh.isdigit()
            and mm.isdigit()
            and 0 <= int(hh) <= 23
            and 0 <= int(mm) <= 59
        )

    @staticmethod
    def _normalize_hhmm(s: Optional[str]) -> Optional[str]:
        if not s:
            return None
        s = s.strip()
        return s if ScheduleReadModel._is_hhmm(s) else None

    def list_schedules_for_teacher_paginated(
        self,
        teacher_id: ObjectId | str,
        page: int = 1,
        page_size: int = 10,
        sort: Optional[List[tuple[str, int]]] = None,
        class_id: Optional[str] = None,
        day_of_week: Optional[int] = None,
        start_time_from: Optional[str] = None,
        start_time_to: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        oid = self._oid(teacher_id)

        page = max(1, int(page))
        page_size = min(max(1, int(page_size)), 100)
        skip = (page - 1) * page_size

        query = not_deleted({"teacher_id": oid})

        if class_id:
            query["class_id"] = self._oid(class_id)

        if day_of_week:
            query["day_of_week"] = int(day_of_week)

      
        st_from = self._normalize_hhmm(start_time_from)
        st_to = self._normalize_hhmm(start_time_to)

        if st_from or st_to:
            query["start_time"] = {}
            if st_from:
                query["start_time"]["$gte"] = st_from
            if st_to:
                query["start_time"]["$lte"] = st_to

            if not query["start_time"]:
                query.pop("start_time", None)

        if sort is None:
            sort = [("day_of_week", 1), ("start_time", 1), ("_id", 1)]

        try:
            total = self.collection.count_documents(query)
            cursor = (
                self.collection.find(query)
                .sort(sort)
                .skip(skip)
                .limit(page_size)
            )
            return list(cursor), total
        except Exception as e:
            self._handle_mongo_error("list_schedules_for_teacher_paginated", e)
            return [], 0

            
    def list_schedules_for_subject(self, subject_id: ObjectId | str) -> List[Dict[str, Any]]:
        oid = self._oid(subject_id)
        try:
            cursor = self.collection.find(not_deleted({"subject_id": oid}))
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_schedules_for_subject", e)
            return []

    def count_lessons_for_date(self, date: dt.date) -> int:
        weekday = date.isoweekday()
        query = not_deleted({"day_of_week": weekday})
        try:
            return self.collection.count_documents(query)
        except Exception as e:
            self._handle_mongo_error("count_lessons_for_date", e)
            return 0

    def has_schedules_for_teacher(self, teacher_id: ObjectId | str, session=None) -> bool:
        oid = self._oid(teacher_id)
        query = not_deleted({"teacher_id": oid})
        return self.collection.find_one(query, session=session) is not None

    def count_schedules_for_teacher(self, teacher_id: Union[ObjectId, str]) -> int:
        oid = self._oid(teacher_id)
        query = not_deleted({"teacher_id": oid})
        try:
            return self.collection.count_documents(query)
        except Exception as e:
            self._handle_mongo_error("count_schedules_for_teacher", e)
            raise

    def aggregate_lessons_by_weekday(self) -> List[Dict[str, Any]]:
        pipeline: List[Dict[str, Any]] = [
            {"$match": not_deleted()},
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
            {"$sort": {"day_of_week": 1}},
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_lessons_by_weekday", e)
            return []

    def aggregate_lessons_by_teacher(self, limit: int = 10) -> List[Dict[str, Any]]:
        if limit <= 0:
            limit = 10

        pipeline: List[Dict[str, Any]] = [
            {"$match": not_deleted()},
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
            {"$sort": {"lesson_count": -1}},
            {"$limit": int(limit)},
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_lessons_by_teacher", e)
            return []