# app/contexts/school/read_models/attendance_read_model.py
from __future__ import annotations

from datetime import datetime, date as date_type, time, timedelta
from typing import Optional, List, Dict, Union, Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.shared.lifecycle.filters import ShowDeleted, by_show_deleted, FIELDS
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.school.domain.attendance import AttendanceStatus, today_kh


class AttendanceReadModel(MongoErrorMixin):
    """
    Canonical persisted date field:
      - record_date = "YYYY-MM-DD" string (recommended)

    Backward compatible:
      - record_date may be datetime (midnight)
      - legacy field: date (datetime midnight)

    Recommended schema for subject/slot attendance:
      attendance: {
        student_id,
        class_id,
        subject_id,
        schedule_slot_id,
        status,
        record_date,             # "YYYY-MM-DD" string (canonical)
        marked_by_teacher_id,
        lifecycle...
      }
    """

    def __init__(self, db: Database):
        self._collection: Collection = db["attendance"]

    # -----------------------------
    # Helpers
    # -----------------------------
    def _oid(self, id_: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def get_by_id(self, id_: Union[str, ObjectId]) -> dict | None:
        return self._collection.find_one({"_id": self._oid(id_)})

    @staticmethod
    def _to_midnight_dt(d: Union[date_type, datetime]) -> datetime:
        if isinstance(d, date_type) and not isinstance(d, datetime):
            return datetime.combine(d, time.min)
        return d

    @staticmethod
    def _date_str(d: date_type) -> str:
        return d.isoformat()

    def _q(
        self,
        extra: Optional[Dict[str, Any]] = None,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[str, Any]:
        return by_show_deleted(show_deleted, dict(extra or {}))

    def _date_match_any_storage(self, record_date: date_type) -> Dict[str, Any]:
        """
        Match canonical + legacy storage formats for record date.
        - record_date: "YYYY-MM-DD" string
        - record_date: datetime midnight (legacy)
        - date: datetime midnight (legacy)
        """
        dt0 = self._to_midnight_dt(record_date)
        s = self._date_str(record_date)
        return {
            "$or": [
                {"record_date": s},      # canonical string
                {"record_date": dt0},    # legacy datetime
                {"date": dt0},           # legacy field
            ]
        }

    # -----------------------------
    # Date normalization for aggregations
    # -----------------------------
    def _normalized_record_date_add_fields_stage(self) -> Dict[str, Any]:
        """
        Produces record_date_dt as BSON Date regardless of:
        - record_date: datetime
        - record_date: "YYYY-MM-DD" string
        - legacy date: datetime
        """
        return {
            "$addFields": {
                "record_date_dt": {
                    "$let": {
                        "vars": {"d": {"$ifNull": ["$record_date", "$date"]}},
                        "in": {
                            "$cond": [
                                {"$eq": [{"$type": "$$d"}, "string"]},
                                {
                                    "$dateFromString": {
                                        "dateString": "$$d",
                                        "format": "%Y-%m-%d",
                                        "timezone": "Asia/Phnom_Penh",
                                        "onError": None,
                                        "onNull": None,
                                    }
                                },
                                {
                                    "$convert": {
                                        "input": "$$d",
                                        "to": "date",
                                        "onError": None,
                                        "onNull": None,
                                    }
                                },
                            ]
                        },
                    }
                }
            }
        }

    def _normalized_record_date_match_stage(self) -> Dict[str, Any]:
        return {"$match": {"record_date_dt": {"$ne": None}}}

    def _range_match_on_normalized_date(
        self,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> Dict[str, Any] | None:
        if not (date_from or date_to):
            return None

        rng: Dict[str, Any] = {}
        if date_from:
            rng["$gte"] = date_from
        if date_to:
            # if date_to at midnight -> treat as inclusive date and move to next day
            if date_to.time() == time.min:
                date_to = date_to + timedelta(days=1)
            rng["$lt"] = date_to
        return {"$match": {"record_date_dt": rng}}

    # -----------------------------
    # Queries (single record)
    # -----------------------------
    def get_by_student_class_subject_slot_date(
        self,
        *,
        student_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        subject_id: Union[str, ObjectId],
        schedule_slot_id: Union[str, ObjectId],
        record_date: date_type,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        sid = self._oid(student_id)
        cid = self._oid(class_id)
        subid = self._oid(subject_id)
        slotid = self._oid(schedule_slot_id)

        q = self._q(
            {
                "student_id": sid,
                "class_id": cid,
                "subject_id": subid,
                "schedule_slot_id": slotid,
                **self._date_match_any_storage(record_date),
            },
            show_deleted=show_deleted,
        )
        return self._collection.find_one(q)

    def get_by_student_class_date(
        self,
        student_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        record_date: Optional[date_type] = None,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        """
        Old behavior (class-level attendance, no subject/slot).
        """
        effective_date = record_date or today_kh()
        sid = self._oid(student_id)
        cid = self._oid(class_id)

        q = self._q(
            {
                "student_id": sid,
                "class_id": cid,
                **self._date_match_any_storage(effective_date),
            },
            show_deleted=show_deleted,
        )
        return self._collection.find_one(q)

    # -----------------------------
    # Queries (lists)
    # -----------------------------
    def list_attendance_for_student(
        self,
        student_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        sid = self._oid(student_id)
        q = self._q({"student_id": sid}, show_deleted=show_deleted)
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))

    def list_attendance_for_teacher(
        self,
        teacher_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        tid = self._oid(teacher_id)
        q = self._q(
            {
                "$or": [
                    {"marked_by_teacher_id": tid},
                    {"teacher_id": tid},  # legacy compatibility
                ]
            },
            show_deleted=show_deleted,
        )
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))

    def list_attendance_for_class(
        self,
        class_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        cid = self._oid(class_id)
        q = self._q({"class_id": cid}, show_deleted=show_deleted)
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))


    def list_attendance_for_class_by_date(
        self,
        class_id: Union[str, ObjectId],
        *,
        record_date: Union[date_type, str, None] = None,
        subject_id: Union[str, ObjectId, None] = None,
        subject_ids: Optional[List[Union[str, ObjectId]]] = None,  # NEW
        schedule_slot_id: Union[str, ObjectId, None] = None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        cid = self._oid(class_id)
        extra: Dict[str, Any] = {"class_id": cid}

        # subject filters
        if subject_id is not None and str(subject_id).strip() != "":
            extra["subject_id"] = self._oid(subject_id)
        elif subject_ids:
            # allow multiple subjects (for non-homeroom teachers)
            values: List[Any] = []
            for sid in subject_ids:
                if sid is None:
                    continue
                oid = self._oid(sid)
                values.append(oid)
                values.append(str(oid))  # tolerate string storage
            if values:
                extra["subject_id"] = {"$in": values}

        # slot filter
        if schedule_slot_id is not None and str(schedule_slot_id).strip() != "":
            slot_oid = self._oid(schedule_slot_id)
            extra["schedule_slot_id"] = {"$in": [slot_oid, str(slot_oid)]}

        # no date => latest by created_at
        if record_date is None or str(record_date).strip() == "":
            q = self._q(extra, show_deleted=show_deleted)
            return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))

        if isinstance(record_date, str):
            record_date = datetime.strptime(record_date, "%Y-%m-%d").date()

        q = self._q(
            {
                **extra,
                **self._date_match_any_storage(record_date),
            },
            show_deleted=show_deleted,
        )
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))
    # -----------------------------
    # Latest (DEFAULT: latest by record_date)
    # -----------------------------
    def get_latest_attendance(
        self,
        *,
        class_id: Union[str, ObjectId] | None = None,
        student_id: Union[str, ObjectId] | None = None,
        teacher_id: Union[str, ObjectId] | None = None,
        subject_id: Union[str, ObjectId] | None = None,
        schedule_slot_id: Union[str, ObjectId] | None = None,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        """
        Latest by normalized record_date (record_date_dt), tie-break by _id.
        """
        extra: Dict[str, Any] = {}

        if class_id is not None:
            extra["class_id"] = self._oid(class_id)

        if student_id is not None:
            extra["student_id"] = self._oid(student_id)

        if subject_id is not None:
            extra["subject_id"] = self._oid(subject_id)

        if schedule_slot_id is not None:
            extra["schedule_slot_id"] = self._oid(schedule_slot_id)

        if teacher_id is not None:
            tid = self._oid(teacher_id)
            extra["$or"] = [{"marked_by_teacher_id": tid}, {"teacher_id": tid}]

        docs = list(
            self._collection.aggregate(
                [
                    {"$match": self._q(extra, show_deleted=show_deleted)},
                    self._normalized_record_date_add_fields_stage(),
                    self._normalized_record_date_match_stage(),
                    {"$sort": {"record_date_dt": -1, "_id": -1}},
                    {"$limit": 1},
                ]
            )
        )
        return docs[0] if docs else None

    def list_attendance_for_class_and_student(
        self,
        *,
        class_id: Union[str, ObjectId],
        student_id: Union[str, ObjectId],
        record_date: Union[date_type, str, None] = None,
        subject_id: Union[str, ObjectId, None] = None,
        schedule_slot_id: Union[str, ObjectId, None] = None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        cid = self._oid(class_id)
        sid = self._oid(student_id)

        extra: Dict[str, Any] = {
            "class_id": cid,
            "student_id": sid,
        }

        if subject_id is not None and str(subject_id).strip() != "":
            extra["subject_id"] = self._oid(subject_id)

        if schedule_slot_id is not None and str(schedule_slot_id).strip() != "":
            extra["schedule_slot_id"] = self._oid(schedule_slot_id)

        # if no date => return recent student records for that class
        if record_date is None or str(record_date).strip() == "":
            q = self._q(extra, show_deleted=show_deleted)
            return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))

        if isinstance(record_date, str):
            record_date = datetime.strptime(record_date, "%Y-%m-%d").date()

        q = self._q({**extra, **self._date_match_any_storage(record_date)}, show_deleted=show_deleted)
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))




    # -----------------------------
    # Aggregations
    # -----------------------------

    def aggregate_status_summary(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        class_id: ObjectId | None = None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        try:
            pipeline: List[Dict[str, Any]] = [
                {"$match": self._q({}, show_deleted=show_deleted)},
                self._normalized_record_date_add_fields_stage(),
                self._normalized_record_date_match_stage(),
            ]

            range_stage = self._range_match_on_normalized_date(date_from, date_to)
            if range_stage:
                pipeline.append(range_stage)

            if class_id:
                pipeline.append({"$match": {"class_id": class_id}})

            pipeline.extend(
                [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                    {"$project": {"_id": 0, "status": "$_id", "count": 1}},
                    {"$sort": {"count": -1}},
                ]
            )

            return list(self._collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_status_summary", e)
            raise

    def aggregate_daily_status_counts(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        class_id: ObjectId | None = None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        try:
            pipeline: List[Dict[str, Any]] = [
                {"$match": self._q({}, show_deleted=show_deleted)},
                self._normalized_record_date_add_fields_stage(),
                self._normalized_record_date_match_stage(),
            ]

            range_stage = self._range_match_on_normalized_date(date_from, date_to)
            if range_stage:
                pipeline.append(range_stage)

            if class_id:
                pipeline.append({"$match": {"class_id": class_id}})

            pipeline.extend(
                [
                    {
                        "$group": {
                            "_id": {
                                "date": {
                                    "$dateToString": {
                                        "format": "%Y-%m-%d",
                                        "date": "$record_date_dt",
                                    }
                                },
                                "status": "$status",
                            },
                            "count": {"$sum": 1},
                        }
                    },
                    {
                        "$group": {
                            "_id": "$_id.date",
                            "counts": {"$push": {"k": "$_id.status", "v": "$count"}},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "date": "$_id",
                            "countsObj": {"$arrayToObject": "$counts"},
                        }
                    },
                    {
                        "$project": {
                            "date": 1,
                            AttendanceStatus.PRESENT.value: {
                                "$ifNull": [f"$countsObj.{AttendanceStatus.PRESENT.value}", 0]
                            },
                            AttendanceStatus.ABSENT.value: {
                                "$ifNull": [f"$countsObj.{AttendanceStatus.ABSENT.value}", 0]
                            },
                            AttendanceStatus.EXCUSED.value: {
                                "$ifNull": [f"$countsObj.{AttendanceStatus.EXCUSED.value}", 0]
                            },
                        }
                    },
                    {"$sort": {"date": 1}},
                ]
            )

            return list(self._collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_daily_status_counts", e)
            raise

    def aggregate_top_absent_students(
        self,
        limit: int = 10,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        class_id: str | None = None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        try:
            pipeline: List[Dict[str, Any]] = [
                {"$match": self._q({"status": AttendanceStatus.ABSENT.value}, show_deleted=show_deleted)},
                self._normalized_record_date_add_fields_stage(),
                self._normalized_record_date_match_stage(),
            ]

            range_stage = self._range_match_on_normalized_date(date_from, date_to)
            if range_stage:
                pipeline.append(range_stage)

            if class_id:
                pipeline.append({"$match": {"class_id": ObjectId(class_id)}})

            pipeline.extend(
                [
                    {
                        "$group": {
                            "_id": {"student_id": "$student_id", "class_id": "$class_id"},
                            "absent_count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"absent_count": -1}},
                    {"$limit": int(limit)},
                ]
            )

            docs = list(self._collection.aggregate(pipeline))

            results: List[Dict[str, Any]] = []
            for doc in docs:
                _id = doc.get("_id", {})
                sid = _id.get("student_id")
                cid = _id.get("class_id")
                absent_count = int(doc.get("absent_count", 0))

                results.append(
                    {
                        "student_id": str(sid) if sid is not None else None,
                        "class_id": str(cid) if cid is not None else None,
                        "absent_count": absent_count,
                        "total_records": absent_count,
                    }
                )

            return results
        except Exception as e:
            self._handle_mongo_error("aggregate_top_absent_students", e)
            raise

    def aggregate_status_by_class(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        class_id: ObjectId | None = None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        """
        Returns per-class attendance counts grouped by status, pivoted into:
        {
            "class_id": "<string>",
            "total": <int>,
            "present": <int>,
            "absent": <int>,
            "excused": <int>
        }
        """
        try:
            pipeline: List[Dict[str, Any]] = [
                {"$match": self._q({}, show_deleted=show_deleted)},
                self._normalized_record_date_add_fields_stage(),
                self._normalized_record_date_match_stage(),
            ]

            range_stage = self._range_match_on_normalized_date(date_from, date_to)
            if range_stage:
                pipeline.append(range_stage)

            if class_id:
                pipeline.append({"$match": {"class_id": class_id}})

            pipeline.extend(
                [
                    {
                        "$group": {
                            "_id": {"class_id": "$class_id", "status": "$status"},
                            "count": {"$sum": 1},
                        }
                    },
                    {
                        "$group": {
                            "_id": "$_id.class_id",
                            "counts": {"$push": {"k": "$_id.status", "v": "$count"}},
                            "total": {"$sum": "$count"},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "class_id": {"$toString": "$_id"},
                            "total": 1,
                            "countsObj": {"$arrayToObject": "$counts"},
                        }
                    },
                    {
                        "$project": {
                            "class_id": 1,
                            "total": 1,
                            AttendanceStatus.PRESENT.value: {
                                "$ifNull": [f"$countsObj.{AttendanceStatus.PRESENT.value}", 0]
                            },
                            AttendanceStatus.ABSENT.value: {
                                "$ifNull": [f"$countsObj.{AttendanceStatus.ABSENT.value}", 0]
                            },
                            AttendanceStatus.EXCUSED.value: {
                                "$ifNull": [f"$countsObj.{AttendanceStatus.EXCUSED.value}", 0]
                            },
                        }
                    },
                    {"$sort": {"total": -1}},
                ]
            )

            return list(self._collection.aggregate(pipeline))

        except Exception as e:
            self._handle_mongo_error("aggregate_status_by_class", e)
            raise