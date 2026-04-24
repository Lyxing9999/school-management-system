from __future__ import annotations

from datetime import date, datetime
from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.model_converter import mongo_converter


class OvertimeReadModel:
    def __init__(self, db: Database):
        self.collection = db["hr_overtime_requests"]

    @staticmethod
    def _oid(v) -> ObjectId | None:
        if v is None:
            return None
        return mongo_converter.convert_to_object_id(v)

    @staticmethod
    def _date_str(v: str | date | None) -> str | None:
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        return str(v)

    def _build_base_query(
        self,
        *,
        employee_id: str | ObjectId | None = None,
        employee_ids: list[str | ObjectId] | None = None,
        status: str | None = None,
        include_deleted: bool = False,
        deleted_only: bool = False,
    ) -> dict:
        query: dict = {}

        if employee_id:
            query["employee_id"] = self._oid(employee_id)
        elif employee_ids:
            scoped_ids = [self._oid(item) for item in employee_ids if self._oid(item)]
            query["employee_id"] = {"$in": scoped_ids}

        if status:
            query["status"] = str(status).strip().lower()

        if deleted_only:
            query["lifecycle.deleted_at"] = {"$ne": None}
        elif not include_deleted:
            query["lifecycle.deleted_at"] = None

        return query

    def list_overtime_requests(
        self,
        *,
        employee_id: str | ObjectId | None = None,
        employee_ids: list[str | ObjectId] | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 10,
        include_deleted: bool = False,
        deleted_only: bool = False,
    ) -> tuple[list[dict], int]:
        query = self._build_base_query(
            employee_id=employee_id,
            employee_ids=employee_ids,
            status=status,
            include_deleted=include_deleted,
            deleted_only=deleted_only,
        )

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit

        items = list(
            self.collection.find(query)
            .sort("submitted_at", -1)
            .skip(skip)
            .limit(limit)
        )
        return items, total

    def get_by_id(self, overtime_id: str | ObjectId) -> dict | None:
        return self.collection.find_one({
            "_id": self._oid(overtime_id),
            "lifecycle.deleted_at": None,
        })

    def list_pending_approval(
        self,
        *,
        employee_id: str | ObjectId | None = None,
        employee_ids: list[str | ObjectId] | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], int]:
        query = self._build_base_query(
            employee_id=employee_id,
            employee_ids=employee_ids,
            status="pending",
        )

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit

        items = list(
            self.collection.find(query)
            .sort("submitted_at", 1)
            .skip(skip)
            .limit(limit)
        )
        return items, total

    def list_approved_for_payroll(
        self,
        *,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
        employee_id: str | ObjectId | None = None,
    ) -> list[dict]:
        query = self._build_base_query(
            employee_id=employee_id,
            status="approved",
        )

        start_date_str = self._date_str(start_date)
        end_date_str = self._date_str(end_date)

        if start_date_str or end_date_str:
            query["request_date"] = {}
            if start_date_str:
                query["request_date"]["$gte"] = start_date_str
            if end_date_str:
                query["request_date"]["$lte"] = end_date_str

        return list(
            self.collection.find(query).sort("request_date", 1)
        )

    def get_my_summary(
        self,
        *,
        employee_id: str | ObjectId,
    ) -> dict:
        employee_oid = self._oid(employee_id)
        query = {
            "employee_id": employee_oid,
            "lifecycle.deleted_at": None,
        }

        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_requests": {"$sum": 1},
                    "pending_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                    },
                    "approved_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                    },
                    "rejected_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                    },
                    "cancelled_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "cancelled"]}, 1, 0]}
                    },
                    "approved_hours": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$status", "approved"]},
                                {"$ifNull": ["$approved_hours", 0]},
                                0,
                            ]
                        }
                    },
                    "approved_payment": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$status", "approved"]},
                                {"$ifNull": ["$calculated_payment", 0]},
                                0,
                            ]
                        }
                    },
                }
            },
        ]

        result = list(self.collection.aggregate(pipeline))
        if not result:
            return {
                "total_requests": 0,
                "pending_count": 0,
                "approved_count": 0,
                "rejected_count": 0,
                "cancelled_count": 0,
                "approved_hours": 0.0,
                "approved_payment": 0.0,
            }

        row = result[0]
        row.pop("_id", None)
        return row

    def get_payroll_summary(
        self,
        *,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> dict:
        query = {
            "status": "approved",
            "lifecycle.deleted_at": None,
        }

        start_date_str = self._date_str(start_date)
        end_date_str = self._date_str(end_date)

        if start_date_str or end_date_str:
            query["request_date"] = {}
            if start_date_str:
                query["request_date"]["$gte"] = start_date_str
            if end_date_str:
                query["request_date"]["$lte"] = end_date_str

        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_approved_requests": {"$sum": 1},
                    "total_approved_hours": {"$sum": {"$ifNull": ["$approved_hours", 0]}},
                    "total_approved_payment": {"$sum": {"$ifNull": ["$calculated_payment", 0]}},
                }
            },
        ]

        result = list(self.collection.aggregate(pipeline))
        if not result:
            return {
                "total_approved_requests": 0,
                "total_approved_hours": 0.0,
                "total_approved_payment": 0.0,
            }

        row = result[0]
        row.pop("_id", None)
        return row
