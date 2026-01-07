from abc import ABC, abstractmethod
from datetime import date, datetime, time as time_type
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.school.domain.attendance import AttendanceRecord
from app.contexts.school.mapper.attendance_mapper import AttendanceMapper
from app.contexts.shared.lifecycle.filters import not_deleted
from app.contexts.shared.lifecycle.updates import now_utc


class IAttendanceRepository(ABC):
    @abstractmethod
    def insert(self, record: AttendanceRecord) -> AttendanceRecord: ...

    @abstractmethod
    def update(self, record: AttendanceRecord) -> Optional[AttendanceRecord]: ...

    @abstractmethod
    def find_by_id(self, id: ObjectId) -> Optional[AttendanceRecord]: ...

    @abstractmethod
    def get_by_student_class_date(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
        record_date: date,
    ) -> Optional[AttendanceRecord]: ...

    @abstractmethod
    def list_for_class_and_date(
        self,
        class_id: ObjectId,
        record_date: date,
    ) -> list[AttendanceRecord]: ...

    @abstractmethod
    def list_for_student(self, student_id: ObjectId) -> list[AttendanceRecord]: ...


class MongoAttendanceRepository(IAttendanceRepository):
    def __init__(self, collection: Collection, mapper: AttendanceMapper | None = None):
        self.collection = collection
        self.mapper = mapper or AttendanceMapper()

    @staticmethod
    def _date_iso(d: date) -> str:
        return d.isoformat()

    @staticmethod
    def _midnight_dt(d: date) -> datetime:
        return datetime.combine(d, time_type.min)

    def insert(self, record: AttendanceRecord) -> AttendanceRecord:
        payload = self.mapper.to_persistence(record)
        self.collection.insert_one(payload)
        return record

    def update(self, record: AttendanceRecord) -> Optional[AttendanceRecord]:
        payload = self.mapper.to_persistence(record)
        _id = payload.pop("_id")

        # Ensure lifecycle.updated_at is advanced even if caller forgot to touch()
        payload.setdefault("lifecycle", {})
        payload["lifecycle"]["updated_at"] = now_utc()

        result = self.collection.update_one(
            not_deleted({"_id": _id}),
            {"$set": payload},
        )
        if result.matched_count == 0:
            return None
        return record

    def find_by_id(self, id: ObjectId) -> Optional[AttendanceRecord]:
        doc = self.collection.find_one(not_deleted({"_id": id}))
        return None if not doc else self.mapper.to_domain(doc)

    def get_by_student_class_date(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
        record_date: date,
    ) -> Optional[AttendanceRecord]:
        iso = self._date_iso(record_date)
        dt = self._midnight_dt(record_date)

        doc = self.collection.find_one(
            not_deleted(
                {
                    "student_id": student_id,
                    "class_id": class_id,
                    "$or": [
                        {"record_date": iso},  # canonical
                        {"record_date": dt},   # legacy datetime
                        {"date": dt},          # legacy field
                    ],
                }
            )
        )
        return None if not doc else self.mapper.to_domain(doc)

    def list_for_class_and_date(
        self,
        class_id: ObjectId,
        record_date: date,
    ) -> list[AttendanceRecord]:
        iso = self._date_iso(record_date)
        dt = self._midnight_dt(record_date)

        cursor = self.collection.find(
            not_deleted(
                {
                    "class_id": class_id,
                    "$or": [
                        {"record_date": iso},
                        {"record_date": dt},
                        {"date": dt},
                    ],
                }
            )
        )
        return [self.mapper.to_domain(doc) for doc in cursor]

    def list_for_student(self, student_id: ObjectId) -> list[AttendanceRecord]:
        cursor = self.collection.find(not_deleted({"student_id": student_id}))
        return [self.mapper.to_domain(doc) for doc in cursor]