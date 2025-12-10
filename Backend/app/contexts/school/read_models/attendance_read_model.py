from datetime import datetime, date as date_type, time
from typing import Optional, List, Dict, Union, Any

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.model_converter import mongo_converter


class AttendanceReadModel:
    """
    Read model to check existing attendance records
    and list attendance by various filters.
    """

    def __init__(self, db: Database):
        self._collection: Collection = db["attendance"]

    def _normalize_id(self, id_: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def get_by_student_class_date(
        self,
        student_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        record_date: Optional[date_type] = None,
    ) -> Optional[Dict]:
        """
        Find an attendance record for (student, class, date).

        If record_date is None, treat it as "today" (UTC),
        mirroring the factory's 'default to today' behavior.
        """
        if record_date is None:
            record_date = datetime.utcnow().date()

        if isinstance(record_date, date_type) and not isinstance(record_date, datetime):
            record_dt = datetime.combine(record_date, time.min)
        else:
            record_dt = record_date  # already datetime

        sid = self._normalize_id(student_id)
        cid = self._normalize_id(class_id)

        return self._collection.find_one(
            {
                "student_id": sid,
                "class_id": cid,
                "date": record_dt,
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
        query: Dict = {"class_id": cid}

        if student_id is not None:
            sid = self._normalize_id(student_id)
            query["student_id"] = sid

        return list(self._collection.find(query))

    


    def aggregate_status_summary(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        class_id: ObjectId | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns summary like:
        [
          { "status": "present", "count": 123 },
          { "status": "absent", "count": 45 },
          ...
        ]
        """
        try:
            match: Dict[str, Any] = {}
            if date_from or date_to:
                match["record_date"] = {}
                if date_from:
                    match["record_date"]["$gte"] = date_from
                if date_to:
                    match["record_date"]["$lte"] = date_to
            if class_id:
                match["class_id"] = class_id

            pipeline = []
            if match:
                pipeline.append({"$match": match})

            pipeline.extend(
                [
                    {
                        "$group": {
                            "_id": "$status",
                            "count": {"$sum": 1},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "status": "$_id",
                            "count": 1,
                        }
                    },
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
    ) -> list[dict[str, Any]]:
        """
        [
        { "date": "2025-11-25", "present": 45, "absent": 3, "excused": 2 },
        ...
        ]
        """
        try:
            match: dict[str, Any] = {}
            if date_from or date_to:
                match["record_date"] = {}
                if date_from:
                    match["record_date"]["$gte"] = date_from
                if date_to:
                    match["record_date"]["$lte"] = date_to

            if class_id:
                match["class_id"] = class_id

            pipeline: list[dict[str, Any]] = []
            if match:
                pipeline.append({"$match": match})

            pipeline.extend([
                {
                    "$group": {
                        "_id": {
                            "date": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d",
                                    "date": "$record_date",
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
                            "$push": {
                                "status": "$_id.status",
                                "count": "$count",
                            }
                        },
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "date": "$_id",
                        "present": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "present"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                        "absent": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "absent"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                        "excused": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "excused"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                    }
                },
                {"$sort": {"date": 1}},
            ])

            return list(self._collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_daily_status_counts", e)
            raise

    def aggregate_daily_status_counts(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        class_id: ObjectId | None = None,
    ) -> list[dict[str, Any]]:
        """
        [
        { "date": "2025-11-25", "present": 45, "absent": 3, "excused": 2 },
        ...
        ]
        """
        try:
            match: dict[str, Any] = {}
            if date_from or date_to:
                match["record_date"] = {}
                if date_from:
                    match["record_date"]["$gte"] = date_from
                if date_to:
                    match["record_date"]["$lte"] = date_to

            if class_id:
                match["class_id"] = class_id

            pipeline: list[dict[str, Any]] = []
            if match:
                pipeline.append({"$match": match})

            pipeline.extend([
                {
                    "$group": {
                        "_id": {
                            "date": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d",
                                    "date": "$record_date",
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
                            "$push": {
                                "status": "$_id.status",
                                "count": "$count",
                            }
                        },
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "date": "$_id",
                        "present": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "present"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                        "absent": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "absent"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                        "excused": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "excused"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                    }
                },
                {"$sort": {"date": 1}},
            ])

            return list(self._collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate_daily_status_counts", e)
            raise


    def aggregate_status_by_class(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict[str, Any]]:
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
        """
        try:
            match: dict[str, Any] = {}
            if date_from or date_to:
                match["record_date"] = {}
                if date_from:
                    match["record_date"]["$gte"] = date_from
                if date_to:
                    match["record_date"]["$lte"] = date_to

            pipeline: list[dict[str, Any]] = []
            if match:
                pipeline.append({"$match": match})

            pipeline.extend([
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
                        "counts": {
                            "$push": {
                                "status": "$_id.status",
                                "count": "$count",
                            }
                        },
                        "total": {"$sum": "$count"},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "class_id": {"$toString": "$_id"},
                        "total": 1,
                        "present": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "present"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                        "absent": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "absent"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                        "excused": {
                            "$let": {
                                "vars": {
                                    "found": {
                                        "$first": {
                                            "$filter": {
                                                "input": "$counts",
                                                "as": "c",
                                                "cond": {"$eq": ["$$c.status", "excused"]},
                                            }
                                        }
                                    }
                                },
                                "in": {"$ifNull": ["$$found.count", 0]},
                            }
                        },
                    }
                },
            ])

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
    ) -> list[dict[str, Any]]:
        """
        Returns rows like:
        {
            "student_id": "....",
            "class_id"  : "....",
            "absent_count": 4,
            "total_records": 4, 
        }
        """
        match: dict[str, Any] = {"status": "absent"}

        if date_from is not None:
            match.setdefault("date", {})
            match["date"]["$gte"] = date_from

        if date_to is not None:
            match.setdefault("date", {})
            match["date"]["$lte"] = date_to

        if class_id:
            match["class_id"] = ObjectId(class_id)

        pipeline: list[dict[str, Any]] = [
            {"$match": match},
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
            {"$limit": limit},
        ]

        docs = list(self._collection.aggregate(pipeline))

        results: list[dict[str, Any]] = []
        for doc in docs:
            _id = doc["_id"]
            sid = _id["student_id"]
            cid = _id.get("class_id")

            results.append(
                {
                    "student_id": str(sid),
                    "class_id": str(cid) if cid else None,
                    "absent_count": int(doc.get("absent_count", 0)),
                    # for now: total_records same as absent_count
                    "total_records": int(doc.get("absent_count", 0)),
                }
            )

        return results