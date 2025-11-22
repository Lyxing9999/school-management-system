from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.school.domain.enrollment import Enrollment
from app.contexts.school.mapper.enrollment_mapper import EnrollmentMapper


class IEnrollmentRepository(ABC):
    """Interface for Enrollment repositories."""

    @abstractmethod
    def insert(self, enrollment: Enrollment) -> Enrollment:
        ...

    @abstractmethod
    def update(self, enrollment: Enrollment) -> Optional[Enrollment]:
        ...

    @abstractmethod
    def find_by_id(self, id: ObjectId) -> Optional[Enrollment]:
        ...

    @abstractmethod
    def list_for_student(self, student_id: ObjectId) -> list[Enrollment]:
        ...

    @abstractmethod
    def list_for_class(self, class_id: ObjectId) -> list[Enrollment]:
        ...

    @abstractmethod
    def is_student_enrolled(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
    ) -> bool:
        ...


class MongoEnrollmentRepository(IEnrollmentRepository):
    """MongoDB implementation of IEnrollmentRepository."""

    def __init__(
        self,
        collection: Collection,
        mapper: EnrollmentMapper | None = None,
    ):
        self.collection = collection
        self.mapper = mapper or EnrollmentMapper()

    def insert(self, enrollment: Enrollment) -> Enrollment:
        payload = self.mapper.to_persistence(enrollment)
        self.collection.insert_one(payload)
        return enrollment

    def update(self, enrollment: Enrollment) -> Optional[Enrollment]:
        payload = self.mapper.to_persistence(enrollment)
        _id = payload.pop("_id")

        result = self.collection.update_one(
            {"_id": _id},
            {"$set": payload},
        )
        if result.matched_count == 0:
            return None
        return enrollment

    def find_by_id(self, id: ObjectId) -> Optional[Enrollment]:
        doc = self.collection.find_one({"_id": id})
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def list_for_student(self, student_id: ObjectId) -> list[Enrollment]:
        cursor = self.collection.find({"student_id": student_id})
        return [self.mapper.to_domain(doc) for doc in cursor]

    def list_for_class(self, class_id: ObjectId) -> list[Enrollment]:
        cursor = self.collection.find({"class_id": class_id})
        return [self.mapper.to_domain(doc) for doc in cursor]

    def is_student_enrolled(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
    ) -> bool:
        doc = self.collection.find_one(
            {
                "student_id": student_id,
                "class_id": class_id,
            }
        )
        return doc is not None