from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.school.domain.attendance import AttendanceRecord
from app.contexts.school.mapper.attendance_mapper import AttendanceMapper


class IAttendanceRepository(ABC):
    """Interface for AttendanceRecord repositories."""

    @abstractmethod
    def insert(self, record: AttendanceRecord) -> AttendanceRecord:
        ...

    @abstractmethod
    def update(self, record: AttendanceRecord) -> Optional[AttendanceRecord]:
        ...

    @abstractmethod
    def find_by_id(self, id: ObjectId) -> Optional[AttendanceRecord]:
        ...

    @abstractmethod
    def get_by_student_class_date(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
        record_date: date,
    ) -> Optional[AttendanceRecord]:
        ...

    @abstractmethod
    def list_for_class_and_date(
        self,
        class_id: ObjectId,
        record_date: date,
    ) -> list[AttendanceRecord]:
        ...

    @abstractmethod
    def list_for_student(
        self,
        student_id: ObjectId,
    ) -> list[AttendanceRecord]:
        ...


class MongoAttendanceRepository(IAttendanceRepository):
    """MongoDB implementation of IAttendanceRepository."""

    def __init__(
        self,
        collection: Collection,
        mapper: AttendanceMapper | None = None,
    ):
        self.collection = collection
        self.mapper = mapper or AttendanceMapper()

    def insert(self, record: AttendanceRecord) -> AttendanceRecord:
        payload = self.mapper.to_persistence(record)
        self.collection.insert_one(payload)
        return record

    def update(self, record: AttendanceRecord) -> Optional[AttendanceRecord]:
        payload = self.mapper.to_persistence(record)
        _id = payload.pop("_id")

        result = self.collection.update_one(
            {"_id": _id},
            {"$set": payload},
        )
        if result.matched_count == 0:
            return None
        return record

    def find_by_id(self, id: ObjectId) -> Optional[AttendanceRecord]:
        doc = self.collection.find_one({"_id": id})
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def get_by_student_class_date(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
        record_date: date,
    ) -> Optional[AttendanceRecord]:
        doc = self.collection.find_one(
            {
                "student_id": student_id,
                "class_id": class_id,
                "record_date": record_date,
            }
        )
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def list_for_class_and_date(
        self,
        class_id: ObjectId,
        record_date: date,
    ) -> list[AttendanceRecord]:
        cursor = self.collection.find(
            {"class_id": class_id, "record_date": record_date}
        )
        return [self.mapper.to_domain(doc) for doc in cursor]

    def list_for_student(
        self,
        student_id: ObjectId,
    ) -> list[AttendanceRecord]:
        cursor = self.collection.find({"student_id": student_id})
        return [self.mapper.to_domain(doc) for doc in cursor]