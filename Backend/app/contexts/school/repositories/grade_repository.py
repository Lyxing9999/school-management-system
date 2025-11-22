from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.school.domain.grade import GradeRecord
from app.contexts.school.mapper.grade_mapper import GradeMapper


class IGradeRepository(ABC):
    """Interface for GradeRecord repositories."""

    @abstractmethod
    def insert(self, grade: GradeRecord) -> GradeRecord:
        ...

    @abstractmethod
    def update(self, grade: GradeRecord) -> Optional[GradeRecord]:
        ...

    @abstractmethod
    def find_by_id(self, id: ObjectId) -> Optional[GradeRecord]:
        ...

    @abstractmethod
    def list_by_student(
        self,
        student_id: ObjectId,
        subject_id: ObjectId | None = None,
        class_id: ObjectId | None = None,
    ) -> list[GradeRecord]:
        ...

    @abstractmethod
    def list_by_class_and_subject(
        self,
        class_id: ObjectId,
        subject_id: ObjectId,
    ) -> list[GradeRecord]:
        ...


class MongoGradeRepository(IGradeRepository):
    """MongoDB implementation of IGradeRepository."""

    def __init__(
        self,
        collection: Collection,
        mapper: GradeMapper | None = None,
    ):
        self.collection = collection
        self.mapper = mapper or GradeMapper()

    def insert(self, grade: GradeRecord) -> GradeRecord:
        payload = self.mapper.to_persistence(grade)
        self.collection.insert_one(payload)
        return grade

    def update(self, grade: GradeRecord) -> Optional[GradeRecord]:
        payload = self.mapper.to_persistence(grade)
        _id = payload.pop("_id")

        result = self.collection.update_one(
            {"_id": _id},
            {"$set": payload},
        )
        if result.matched_count == 0:
            return None
        return grade

    def find_by_id(self, id: ObjectId) -> Optional[GradeRecord]:
        doc = self.collection.find_one({"_id": id})
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def list_by_student(
        self,
        student_id: ObjectId,
        subject_id: ObjectId | None = None,
        class_id: ObjectId | None = None,
    ) -> list[GradeRecord]:
        query: dict = {"student_id": student_id}
        if subject_id is not None:
            query["subject_id"] = subject_id
        if class_id is not None:
            query["class_id"] = class_id

        cursor = self.collection.find(query)
        return [self.mapper.to_domain(doc) for doc in cursor]

    def list_by_class_and_subject(
        self,
        class_id: ObjectId,
        subject_id: ObjectId,
    ) -> list[GradeRecord]:
        cursor = self.collection.find(
            {"class_id": class_id, "subject_id": subject_id}
        )
        return [self.mapper.to_domain(doc) for doc in cursor]