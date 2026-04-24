from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database

from app.contexts.hrms.domain.leave import LeaveRequest
from app.contexts.hrms.errors.leave_exceptions import LeaveNotFoundException
from app.contexts.hrms.mapper.leave_mapper import LeaveMapper


class MongoLeaveRepository:
    def __init__(self, db: Database):
        self.collection = db["hr_leave_requests"]
        self.mapper = LeaveMapper()

    @staticmethod
    def _oid(v) -> ObjectId | None:
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return v
        return ObjectId(v)

    def save(self, leave: LeaveRequest) -> LeaveRequest:
        doc = self.mapper.to_persistence(leave)
        self.collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        return self.find_by_id(doc["_id"])

    def find_by_id(self, leave_id) -> LeaveRequest:
        doc = self.collection.find_one({"_id": self._oid(leave_id)})
        if not doc:
            raise LeaveNotFoundException(str(leave_id))
        return self.mapper.to_domain(doc)

    def list_requests(
        self,
        *,
        employee_id: ObjectId | None = None,
        employee_ids: list[ObjectId] | None = None,
        status: str | None = None,
        include_deleted: bool = False,
        deleted_only: bool = False,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[LeaveRequest], int]:
        query = {}

        if employee_id:
            query["employee_id"] = self._oid(employee_id)
        elif employee_ids:
            query["employee_id"] = {
                "$in": [self._oid(item) for item in employee_ids if self._oid(item)]
            }
        if status:
            query["status"] = status

        if deleted_only:
            query["lifecycle.deleted_at"] = {"$ne": None}
        elif not include_deleted:
            query["lifecycle.deleted_at"] = None

        total = self.collection.count_documents(query)
        skip = (page - 1) * page_size

        docs = list(
            self.collection.find(query)
            .sort("start_date", -1)
            .skip(skip)
            .limit(page_size)
        )
        return [self.mapper.to_domain(x) for x in docs], total

    def find_overlapping_approved_or_pending(
        self,
        *,
        employee_id: ObjectId,
        start_date,
        end_date,
    ) -> LeaveRequest | None:
        doc = self.collection.find_one({
            "employee_id": self._oid(employee_id),
            "status": {"$in": ["pending", "approved"]},
            "start_date": {"$lte": end_date.isoformat()},
            "end_date": {"$gte": start_date.isoformat()},
            "lifecycle.deleted_at": None,
        })
        return self.mapper.to_domain(doc) if doc else None
    
    def list_approved_by_employee_and_month(self, *, employee_id, month: str):
        year, month_num = map(int, month.split("-"))
        month_start = f"{year:04d}-{month_num:02d}-01"
        from calendar import monthrange
        month_end = f"{year:04d}-{month_num:02d}-{monthrange(year, month_num)[1]:02d}"

        docs = list(
            self.collection.find({
                "employee_id": self._oid(employee_id),
                "status": "approved",
                "lifecycle.deleted_at": None,
                "start_date": {"$lte": month_end},
                "end_date": {"$gte": month_start},
            }).sort("start_date", 1)
        )
        return [self.mapper.to_domain(x) for x in docs]
