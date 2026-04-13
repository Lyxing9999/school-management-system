from __future__ import annotations

from bson import ObjectId
from datetime import datetime, date
from calendar import monthrange
from pymongo.database import Database

from app.contexts.hrms.domain.attendance import Attendance
from app.contexts.hrms.mapper.attendance_mapper import AttendanceMapper
from app.contexts.hrms.errors.attendance_exceptions import AttendanceNotFoundException


class MongoAttendanceRepository:
    def __init__(self, db: Database):
        self.collection = db["hr_attendances"]
        self.mapper = AttendanceMapper()

    def _oid(self, value) -> ObjectId | None:
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
        return ObjectId(value)

    def save(self, attendance: Attendance) -> Attendance:
        doc = self.mapper.to_persistence(attendance)
        self.collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        return attendance

    def find_by_id(self, attendance_id) -> Attendance:
        doc = self.collection.find_one({"_id": self._oid(attendance_id)})
        if not doc:
            raise AttendanceNotFoundException(attendance_id)
        return self.mapper.to_domain(doc)

    def find_by_employee_and_date(self, employee_id, attendance_date: datetime) -> Attendance | None:
        doc = self.collection.find_one({
            "employee_id": self._oid(employee_id),
            "attendance_date": attendance_date,
            "lifecycle.deleted_at": None,
        })
        return self.mapper.to_domain(doc) if doc else None

    def list_open_attendances(self) -> list[Attendance]:
        docs = self.collection.find({
            "check_in_time": {"$ne": None},
            "check_out_time": None,
            "lifecycle.deleted_at": None,
        })
        return [self.mapper.to_domain(doc) for doc in docs]

    def list_by_employee_and_month(self, *, employee_id, month: str) -> list[Attendance]:
        year, month_num = map(int, month.split("-"))
        month_start = date(year, month_num, 1)
        month_end = date(year, month_num, monthrange(year, month_num)[1])

        start_key = month_start.isoformat()
        end_key = month_end.isoformat()

        docs = list(
            self.collection.find({
                "employee_id": self._oid(employee_id),
                "lifecycle.deleted_at": None,
                "attendance_date_local": {
                    "$gte": start_key,
                    "$lte": end_key,
                },
            }).sort("attendance_date_local", 1)
        )
        return [self.mapper.to_domain(doc) for doc in docs]

    def delete(self, attendance_id) -> None:
        self.collection.delete_one({"_id": self._oid(attendance_id)})