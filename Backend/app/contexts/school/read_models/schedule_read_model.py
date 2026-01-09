import datetime as dt
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, Set

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.cursor import Cursor

from app.contexts.core.errors import MongoErrorMixin
from app.contexts.shared.lifecycle.filters import ShowDeleted, by_show_deleted, not_deleted
from app.contexts.shared.model_converter import mongo_converter


_MAX_PAGE_SIZE = 100


class ScheduleReadModel(MongoErrorMixin):
    """
    Read-only access for schedule documents.
    Returned objects are plain dicts (Mongo docs), not domain aggregates.

    IMPORTANT:
    - Uses `show_deleted` consistently via `by_show_deleted(...)`.
    - Supports legacy stored IDs (ObjectId or string) for teacher/class/subject.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["schedules"]

    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def _oid_optional(self, id_: str | ObjectId | None) -> Optional[ObjectId]:
        if id_ is None:
            return None
        if isinstance(id_, str) and not id_.strip():
            return None
        return self._oid(id_)

    def _normalize_ids(self, ids: Iterable[str | ObjectId]) -> List[ObjectId]:
        out: List[ObjectId] = []
        for v in ids or []:
            if v is None:
                continue
            if isinstance(v, str) and not v.strip():
                continue
            out.append(self._oid(v))
        return out

    def _id_match(self, field: str, oid: ObjectId) -> Dict[str, Any]:
        """
        Supports mixed storage formats: ObjectId OR string(ObjectId).
        If your DB is already clean (ObjectId only), you can simplify to {field: oid}.
        """
        return {field: {"$in": [oid, str(oid)]}}

    def _weekday_candidates(self, dow: int) -> List[int]:
        """
        Supports both ISO 1..7 and 0-based 0..6 if your DB has mixed formats.
        """
        candidates: Set[int] = set()

        if 1 <= dow <= 7:
            candidates.add(dow)       # ISO
            candidates.add(dow - 1)   # 0-based
        elif 0 <= dow <= 6:
            candidates.add(dow)       # 0-based
            candidates.add(dow + 1)   # ISO

        return sorted(candidates)

    # --------------------------
    # Basic reads
    # --------------------------

    def get_by_id(
        self,
        id_: ObjectId | str,
        *,
        show_deleted: ShowDeleted = "active",
        projection: Optional[Dict[str, int]] = None,
        session=None,
    ) -> Dict[str, Any] | None:
        oid = self._oid(id_)
        try:
            query = by_show_deleted(show_deleted, {"_id": oid})
            return self.collection.find_one(query, projection=projection, session=session)
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)
            return None

    def list_all(
        self,
        *,
        show_deleted: ShowDeleted = "active",
        projection: Optional[Dict[str, int]] = None,
        sort: Optional[List[tuple[str, int]]] = None,
        limit: Optional[int] = None,
        session=None,
    ) -> List[Dict[str, Any]]:
        try:
            query = by_show_deleted(show_deleted, {})
            cur = self.collection.find(query, projection=projection, session=session)

            if sort:
                cur = cur.sort(sort)

            if limit is not None:
                cur = cur.limit(int(limit))

            return list(cur)
        except Exception as e:
            self._handle_mongo_error("list_all", e)
            return []
    def list_by_ids(
        self,
        ids: Iterable[str | ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
        projection: Optional[Dict[str, int]] = None,
        session=None,
    ) -> List[Dict[str, Any]]:
        oids = self._normalize_ids(ids)
        if not oids:
            return []

        query = by_show_deleted(show_deleted, {"_id": {"$in": oids}})
        try:
            return list(self.collection.find(query, projection=projection, session=session))
        except Exception as e:
            self._handle_mongo_error("list_by_ids", e)
            return []
    # --------------------------
    # Class schedules
    # --------------------------

    def list_schedules_for_class_paginated(
        self,
        class_id: ObjectId | str,
        page: int = 1,
        page_size: int = 10,
        *,
        show_deleted: ShowDeleted = "active",
        projection: Optional[Dict[str, int]] = None,
        sort: Optional[List[tuple[str, int]]] = None,
        session=None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        cid = self._oid(class_id)

        page = max(1, int(page or 1))
        page_size = min(max(1, int(page_size or 10)), _MAX_PAGE_SIZE)
        skip = (page - 1) * page_size

        # Mixed ID format safe
        base = self._id_match("class_id", cid)
        query = by_show_deleted(show_deleted, base)

        if sort is None:
            sort = [("day_of_week", 1), ("start_time", 1), ("_id", 1)]

        try:
            total = int(self.collection.count_documents(query, session=session))
            cur = (
                self.collection.find(query, projection=projection, session=session)
                .sort(sort)
                .skip(skip)
                .limit(page_size)
            )
            return list(cur), total
        except Exception as e:
            self._handle_mongo_error("list_schedules_for_class_paginated", e)
            return [], 0

    def list_schedules_for_classes(
        self,
        class_ids: Iterable[str | ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
        projection: Optional[Dict[str, int]] = None,
        sort: Optional[List[tuple[str, int]]] = None,
        limit: Optional[int] = None,
        session=None,
    ) -> List[Dict[str, Any]]:
        ids = self._normalize_ids(class_ids)
        if not ids:
            return []

        # Mixed ID format safe
        base = {"class_id": {"$in": ids + [str(x) for x in ids]}}
        query = by_show_deleted(show_deleted, base)

        sort_spec = sort or [("class_id", 1), ("day_of_week", 1), ("start_time", 1), ("_id", 1)]

        try:
            cur: Cursor = self.collection.find(query, projection=projection, session=session).sort(sort_spec)

            if limit is not None:
                cur = cur.limit(int(limit))

            return list(cur)
        except Exception as e:
            self._handle_mongo_error("list_schedules_for_classes", e)
            return []

    # --------------------------
    # Teacher schedules
    # --------------------------

    @staticmethod
    def _is_hhmm(s: str) -> bool:
        if not s or len(s) != 5 or s[2] != ":":
            return False
        hh, mm = s[:2], s[3:]
        return hh.isdigit() and mm.isdigit() and 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59

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
        *,
        show_deleted: ShowDeleted = "active",
        sort: Optional[List[tuple[str, int]]] = None,
        projection: Optional[Dict[str, int]] = None,
        session=None,
        class_id: ObjectId | str | None = None,
        day_of_week: Optional[int] = None,
        start_time_from: Optional[str] = None,
        start_time_to: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        tid = self._oid(teacher_id)

        page = max(1, int(page or 1))
        page_size = min(max(1, int(page_size or 10)), _MAX_PAGE_SIZE)
        skip = (page - 1) * page_size

        base: Dict[str, Any] = {}
        base.update(self._id_match("teacher_id", tid))

        if class_id:
            cid = self._oid(class_id)
            base.update(self._id_match("class_id", cid))

        if day_of_week is not None:
            dow = int(day_of_week)
            base["day_of_week"] = {"$in": self._weekday_candidates(dow)}

        st_from = self._normalize_hhmm(start_time_from)
        st_to = self._normalize_hhmm(start_time_to)
        if st_from or st_to:
            base["start_time"] = {}
            if st_from:
                base["start_time"]["$gte"] = st_from
            if st_to:
                base["start_time"]["$lte"] = st_to
            if not base["start_time"]:
                base.pop("start_time", None)

        query = by_show_deleted(show_deleted, base)

        if sort is None:
            sort = [("day_of_week", 1), ("start_time", 1), ("_id", 1)]

        try:
            total = int(self.collection.count_documents(query, session=session))
            cur = (
                self.collection.find(query, projection=projection, session=session)
                .sort(sort)
                .skip(skip)
                .limit(page_size)
            )
            return list(cur), total
        except Exception as e:
            self._handle_mongo_error("list_schedules_for_teacher_paginated", e)
            return [], 0

    # --------------------------
    # Subject schedules
    # --------------------------

    def list_schedules_for_subject(
        self,
        subject_id: ObjectId | str,
        *,
        show_deleted: ShowDeleted = "active",
        projection: Optional[Dict[str, int]] = None,
        sort: Optional[List[tuple[str, int]]] = None,
        limit: Optional[int] = None,
        session=None,
    ) -> List[Dict[str, Any]]:
        sid = self._oid(subject_id)

        base = self._id_match("subject_id", sid)
        query = by_show_deleted(show_deleted, base)

        sort_spec = sort or [("day_of_week", 1), ("start_time", 1), ("_id", 1)]

        try:
            cur = self.collection.find(query, projection=projection, session=session).sort(sort_spec)
            if limit is not None:
                cur = cur.limit(int(limit))
            return list(cur)
        except Exception as e:
            self._handle_mongo_error("list_schedules_for_subject", e)
            return []

    # --------------------------
    # Counts / checks
    # --------------------------

    def count_lessons_for_date(
        self,
        date: dt.date,
        *,
        show_deleted: ShowDeleted = "active",
        session=None,
    ) -> int:
        # ISO weekday (1..7)
        weekday = int(date.isoweekday())
        base = {"day_of_week": {"$in": self._weekday_candidates(weekday)}}
        query = by_show_deleted(show_deleted, base)
        try:
            return int(self.collection.count_documents(query, session=session))
        except Exception as e:
            self._handle_mongo_error("count_lessons_for_date", e)
            return 0

    def has_schedules_for_teacher(
        self,
        teacher_id: ObjectId | str,
        *,
        show_deleted: ShowDeleted = "active",
        session=None,
    ) -> bool:
        tid = self._oid(teacher_id)
        base = self._id_match("teacher_id", tid)
        query = by_show_deleted(show_deleted, base)
        try:
            return self.collection.find_one(query, session=session) is not None
        except Exception as e:
            self._handle_mongo_error("has_schedules_for_teacher", e)
            return False

    def count_schedules_for_teacher(
        self,
        teacher_id: Union[ObjectId, str],
        *,
        show_deleted: ShowDeleted = "active",
        session=None,
    ) -> int:
        tid = self._oid(teacher_id)
        base = self._id_match("teacher_id", tid)
        query = by_show_deleted(show_deleted, base)
        try:
            return int(self.collection.count_documents(query, session=session))
        except Exception as e:
            self._handle_mongo_error("count_schedules_for_teacher", e)
            return 0

    # --------------------------
    # Aggregations
    # --------------------------

    def aggregate_lessons_by_weekday(
        self,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        pipeline: List[Dict[str, Any]] = [
            {"$match": by_show_deleted(show_deleted, {})},
            {"$group": {"_id": "$day_of_week", "lesson_count": {"$sum": 1}}},
            {"$project": {"_id": 0, "day_of_week": "$_id", "lesson_count": 1}},
            {"$sort": {"day_of_week": 1}},
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_lessons_by_weekday", e)
            return []

    def aggregate_lessons_by_teacher(
        self,
        limit: int = 10,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        if limit <= 0:
            limit = 10

        pipeline: List[Dict[str, Any]] = [
            {"$match": by_show_deleted(show_deleted, {})},
            {"$group": {"_id": "$teacher_id", "lesson_count": {"$sum": 1}}},
            {"$project": {"_id": 0, "teacher_id": {"$toString": "$_id"}, "lesson_count": 1}},
            {"$sort": {"lesson_count": -1}},
            {"$limit": int(limit)},
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_lessons_by_teacher", e)
            return []