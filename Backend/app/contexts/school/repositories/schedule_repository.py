from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.school.domain.schedule import ScheduleSlot, DayOfWeek
from app.contexts.school.mapper.schedule_mapper import ScheduleMapper


class IScheduleRepository(ABC):
    """Interface for ScheduleSlot repositories."""

    @abstractmethod
    def insert(self, slot: ScheduleSlot) -> ScheduleSlot:
        ...

    @abstractmethod
    def update(self, slot: ScheduleSlot) -> Optional[ScheduleSlot]:
        ...

    @abstractmethod
    def delete(self, id: ObjectId) -> bool:
        ...

    @abstractmethod
    def find_by_id(self, id: ObjectId) -> Optional[ScheduleSlot]:
        ...

    @abstractmethod
    def list_for_class(self, class_id: ObjectId) -> list[ScheduleSlot]:
        ...

    @abstractmethod
    def list_for_teacher(self, teacher_id: ObjectId) -> list[ScheduleSlot]:
        ...

    @abstractmethod
    def list_for_teacher_and_day(
        self,
        teacher_id: ObjectId,
        day_of_week: DayOfWeek | int,
    ) -> list[ScheduleSlot]:
        ...


class MongoScheduleRepository(IScheduleRepository):
    """MongoDB implementation of IScheduleRepository."""

    def __init__(
        self,
        collection: Collection,
        mapper: ScheduleMapper | None = None,
    ):
        self.collection = collection
        self.mapper = mapper or ScheduleMapper()

    def insert(self, slot: ScheduleSlot) -> ScheduleSlot:
        payload = self.mapper.to_persistence(slot)
        self.collection.insert_one(payload)
        return slot

    def update(self, slot: ScheduleSlot) -> Optional[ScheduleSlot]:
        payload = self.mapper.to_persistence(slot)
        _id = payload.pop("_id")

        result = self.collection.update_one(
            {"_id": _id},
            {"$set": payload},
        )
        if result.matched_count == 0:
            return None
        return slot

    def delete(self, id: ObjectId) -> bool:
        result = self.collection.delete_one({"_id": id})
        return result.deleted_count == 1

    def find_by_id(self, id: ObjectId) -> Optional[ScheduleSlot]:
        doc = self.collection.find_one({"_id": id})
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def list_for_class(self, class_id: ObjectId) -> list[ScheduleSlot]:
        cursor = self.collection.find({"class_id": class_id})
        return [self.mapper.to_domain(doc) for doc in cursor]

    def list_for_teacher(self, teacher_id: ObjectId) -> list[ScheduleSlot]:
        cursor = self.collection.find({"teacher_id": teacher_id})
        return [self.mapper.to_domain(doc) for doc in cursor]

    def list_for_teacher_and_day(
        self,
        teacher_id: ObjectId,
        day_of_week: DayOfWeek | int,
    ) -> list[ScheduleSlot]:
        day_value = int(day_of_week)
        cursor = self.collection.find(
            {"teacher_id": teacher_id, "day_of_week": day_value}
        )
        return [self.mapper.to_domain(doc) for doc in cursor]