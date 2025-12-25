from __future__ import annotations

from datetime import datetime, date as date_type, time
from typing import Optional, List, Dict, Union, Any

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin


class AttendanceReadModel(MongoErrorMixin):
    """
    Read model to check existing attendance records
    and list/aggregate attendance by various filters.

    Canonical date field: `record_date` (datetime).
    Backward-compatible with legacy field: `date` (datetime).
    """

    def __init__(self, db: Database):
        self._collection: Collection = db["attendance"]

    def _normalize_id(self, id_: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def _to_midnight_dt(self, d: Union[date_type, datetime]) -> datetime:
        """
        Normalize a date or datetime to a datetime at 00:00:00.
        """
        if isinstance(d, date_type) and not isinstance(d, datetime):
            return datetime.combine(d, time.min)
        # if it is datetime already, keep as-is (caller can pass midnight if desired)
        return d

    def _normalized_record_date_add_fields_stage(self) -> Dict[str, Any]:
        """
        Adds `record_date_dt` as a safe datetime converted from `record_date` or legacy `date`.
        """
        return {
            "$addFields": {
                "record_date_dt": {
                    "$convert": {
                        "input": {"$ifNull": ["$record_date", "$date"]},
                        "to": "date",
                        "onError": None,
                        "onNull": None,
                    }
                }
            }
        }

    def _normalized_record_date_match_stage(self) -> Dict[str, Any]:
        """
        Ensures `record_date_dt` exists and is a valid datetime.
        """
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
            rng["$lte"] = date_to
        return {"$match": {"record_date_dt": rng}}

    def get_by_student_class_date(
        self,
        student_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        record_date: Optional[date_type] = None,
    ) -> Optional[Dict]:
        """
        Find an attendance record for (student, class, date).

        If record_date is None, treat it as "today" (UTC).
        Backward-compatible: matches either `record_date` or legacy `date`.
        """
        if record_date is None:
            record_date = datetime.utcnow().date()

        record_dt = self._to_midnight_dt(record_date)

        sid = self._normalize_id(student_id)
        cid = self._normalize_id(class_id)

        return self._collection.find_one(
            {
                "student_id": sid,
                "class_id": cid,
                "$or": [
                    {"record_date": record_dt},
                    {"date": record_dt},  # legacy field
                ],
            }
        )

    def list_attendance_for_student(self, student_id: Union[str, ObjectId]) -> List[Dict]:
        sid = self._normalize_id(student_id)
        return list(self._collection.find({"student_id": sid}))

    def list_attendance_for_teacher(self, teacher_id: Union[str, ObjectId]) -> List[Dict]:
        tid = self._normalize_id(teacher_id)
        return list(self._collection.find({"teacher_id": tid}))

    def list_attendance_for_class(self, class_id: Union[str, ObjectId]) -> List[Dict]:
        cid = self._normalize_id(class_id)
        return list(self._collection.find({"class_id": cid}))

    def list_attendance_for_class_and_student(
        self,
        class_id: Union[str, ObjectId],
        student_id: Optional[Union[str, ObjectId]] = None,
    ) -> List[Dict]:
        cid = self._normalize_id(class_id)
        query: Dict[str, Any] = {"class_id": cid}

        if student_id is not None:
            sid = self._normalize_id(student_id)
            query["student_id"] = sid

        return list(self._collection.find(query))

    def aggregate_status_summary(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        class_id: ObjectId | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns summary like:
        [
          { "status": "present", "count": 123 },
          { "status": "absent", "count": 45 },
          ...
        ]

        Uses normalized date field `record_date_dt` (record_date or legacy date).
        """
        try:
            pipeline: List[Dict[str, Any]] = [
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
    ) -> List[Dict[str, Any]]:
        """
        [
          { "date": "2025-11-25", "present": 45, "absent": 3, "excused": 2 },
          ...
        ]

        Uses normalized date field `record_date_dt` (record_date or legacy date),
        preventing `$dateToString` failures when the field is missing/invalid.
        """
        try:
            pipeline: List[Dict[str, Any]] = [
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
                            "counts": {
                                # build key/value pairs directly so we can $arrayToObject
                                "$push": {"k": "$_id.status", "v": "$count"}
                            },
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
                            "present": {"$ifNull": ["$countsObj.present", 0]},
                            "absent": {"$ifNull": ["$countsObj.absent", 0]},
                            "excused": {"$ifNull": ["$countsObj.excused", 0]},
                        }
                    },
                    {"$sort": {"date": 1}},
                ]
            )

            return list(self._collection.aggregate(pipeline))

        except Exception as e:
            self._handle_mongo_error("aggregate_daily_status_counts", e)
            raise

    def aggregate_status_by_class(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> List[Dict[str, Any]]:
        """
        [
          {
            "class_id": "69253bc39e97249bcea9ae28",
            "present": 30,
            "absent": 5,
            "excused": 2,
            "total": 37
          },
          ...
        ]

        Uses normalized date field `record_date_dt` (record_date or legacy date).
        """
        try:
            pipeline: List[Dict[str, Any]] = [
                self._normalized_record_date_add_fields_stage(),
                self._normalized_record_date_match_stage(),
            ]

            range_stage = self._range_match_on_normalized_date(date_from, date_to)
            if range_stage:
                pipeline.append(range_stage)

            pipeline.extend(
                [
                    {
                        "$group": {
                            "_id": {
                                "class_id": "$class_id",
                                "status": "$status",
                            },
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
                            "present": {"$ifNull": ["$countsObj.present", 0]},
                            "absent": {"$ifNull": ["$countsObj.absent", 0]},
                            "excused": {"$ifNull": ["$countsObj.excused", 0]},
                        }
                    },
                    {"$sort": {"total": -1}},
                ]
            )

            return list(self._collection.aggregate(pipeline))

        except Exception as e:
            self._handle_mongo_error("aggregate_status_by_class", e)
            raise

    def aggregate_top_absent_students(
        self,
        limit: int = 10,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        class_id: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns rows like:
        {
          "student_id": "...",
          "class_id": "...",
          "absent_count": 4,
          "total_records": 4
        }

        Uses normalized date field `record_date_dt` (record_date or legacy date).
        """
        try:
            pipeline: List[Dict[str, Any]] = [
                self._normalized_record_date_add_fields_stage(),
                self._normalized_record_date_match_stage(),
                {"$match": {"status": "absent"}},
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
                            "_id": {
                                "student_id": "$student_id",
                                "class_id": "$class_id",
                            },
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