from __future__ import annotations

from bson import ObjectId
from datetime import datetime, timedelta
from pymongo.database import Database

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.time_utils import (
    cambodia_start_of_day_as_utc,
    ensure_utc,
    utc_now,
)


class AttendanceReadModel:
    def __init__(self, db: Database):
        self.collection = db["hr_attendances"]

    @staticmethod
    def _oid(value) -> ObjectId | None:
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and value.strip().lower() in {
            "",
            "null",
            "none",
            "undefined",
        }:
            return None
        return mongo_converter.convert_to_object_id(value)

    def find_by_id(self, attendance_id) -> dict | None:
        return self.collection.find_one({"_id": self._oid(attendance_id)})

    def find_by_employee_today(self, employee_id) -> dict | None:
        start_of_day = cambodia_start_of_day_as_utc(utc_now())
        return self.collection.find_one({
            "employee_id": self._oid(employee_id),
            "attendance_date": start_of_day,
            "lifecycle.deleted_at": None,
        })

    def list_attendances(
        self,
        *,
        employee_id=None,
        employee_ids: list | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        status: str | None = None,
        include_deleted: bool = False,
        deleted_only: bool = False,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], int]:
        query = {}

        if employee_id:
            query["employee_id"] = self._oid(employee_id)

        if employee_ids:
            query["employee_id"] = {
                "$in": [self._oid(item) for item in employee_ids if self._oid(item)]
            }

        if start_date or end_date:
            query["check_in_time"] = {}
            if start_date:
                query["check_in_time"]["$gte"] = ensure_utc(start_date)
            if end_date:
                query["check_in_time"]["$lte"] = ensure_utc(end_date)

        if status:
            normalized_status = str(status).strip().lower()
            wrong_location_status_map = {
                "wrong_location_pending": "pending",
                "wrong_location_approved": "approved",
                "wrong_location_rejected": "rejected",
            }
            if normalized_status in wrong_location_status_map:
                query["$or"] = [
                    {"location_review_status": wrong_location_status_map[normalized_status]},
                    {"status": normalized_status},
                ]
            else:
                query["status"] = normalized_status

        if deleted_only:
            query["lifecycle.deleted_at"] = {"$ne": None}
        elif not include_deleted:
            query["lifecycle.deleted_at"] = None

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit

        docs = list(
            self.collection.find(query)
            .sort("check_in_time", -1)
            .skip(skip)
            .limit(limit)
        )
        return docs, total

    def get_employee_stats(self, *, employee_id, start_date: datetime, end_date: datetime) -> dict:
        start_date_utc = ensure_utc(start_date)
        end_date_utc = ensure_utc(end_date)

        pipeline = [
            {
                "$match": {
                    "employee_id": self._oid(employee_id),
                    "check_in_time": {"$gte": start_date_utc, "$lte": end_date_utc},
                    "lifecycle.deleted_at": None,
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_days": {"$sum": 1},
                    "late_days": {
                        "$sum": {"$cond": [{"$gt": ["$late_minutes", 0]}, 1, 0]}
                    },
                    "early_leave_days": {
                        "$sum": {"$cond": [{"$gt": ["$early_leave_minutes", 0]}, 1, 0]}
                    },
                    "total_late_minutes": {"$sum": "$late_minutes"},
                    "total_early_leave_minutes": {"$sum": "$early_leave_minutes"},
                }
            },
        ]

        result = list(self.collection.aggregate(pipeline))
        if not result:
            return {
                "total_days": 0,
                "present_days": 0,
                "late_days": 0,
                "early_leave_days": 0,
                "total_late_minutes": 0,
                "total_early_leave_minutes": 0,
                "attendance_rate": 0.0,
            }

        stats = result[0]
        total_days = stats["total_days"]
        expected_days = (end_date_utc - start_date_utc).days + 1

        return {
            "total_days": total_days,
            "present_days": total_days,
            "late_days": stats["late_days"],
            "early_leave_days": stats["early_leave_days"],
            "total_late_minutes": stats["total_late_minutes"],
            "total_early_leave_minutes": stats["total_early_leave_minutes"],
            "attendance_rate": (total_days / expected_days * 100) if expected_days > 0 else 0.0,
        }

    def list_wrong_location_cases(
        self,
        *,
        start_date=None,
        end_date=None,
        review_status: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], int]:
        query = {
            "lifecycle.deleted_at": None,
            "$or": [
                {"location_review_status": {"$in": ["pending", "approved", "rejected"]}},
                {"status": {"$in": [
                    "wrong_location_pending",
                    "wrong_location_approved",
                    "wrong_location_rejected",
                ]}},
                {"wrong_location_reason": {"$ne": None}},
            ],
        }

        if review_status:
            normalized = review_status.strip().lower()
            legacy_map = {
                "wrong_location_pending": "pending",
                "wrong_location_approved": "approved",
                "wrong_location_rejected": "rejected",
            }
            normalized_review_status = legacy_map.get(normalized, normalized)
            query["$and"] = [
                {
                    "$or": [
                        {"location_review_status": normalized_review_status},
                        {"status": f"wrong_location_{normalized_review_status}"},
                    ]
                }
            ]

        if start_date or end_date:
            query["check_in_time"] = {}
            if start_date:
                query["check_in_time"]["$gte"] = ensure_utc(start_date)
            if end_date:
                query["check_in_time"]["$lte"] = ensure_utc(end_date)

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit

        items = list(
            self.collection.find(query)
            .sort("check_in_time", -1)
            .skip(skip)
            .limit(limit)
        )
        return items, total
