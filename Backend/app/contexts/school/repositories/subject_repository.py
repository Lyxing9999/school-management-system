from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.school.domain.subject import Subject
from app.contexts.school.mapper.subject_mapper import SubjectMapper


class ISubjectRepository(ABC):
    """Interface for Subject repositories."""

    @abstractmethod
    def insert(self, subject: Subject) -> Subject:
        ...

    @abstractmethod
    def update(self, subject: Subject) -> Optional[Subject]:
        ...

    @abstractmethod
    def find_by_id(self, id: ObjectId) -> Optional[Subject]:
        ...

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Subject]:
        ...

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Subject]:
        ...

    @abstractmethod
    def list_all(self, active_only: bool = False) -> list[Subject]:
        ...


class MongoSubjectRepository(ISubjectRepository):
    """MongoDB implementation of ISubjectRepository."""

    def __init__(
        self,
        collection: Collection,
        mapper: SubjectMapper | None = None,
    ):
        self.collection = collection
        self.mapper = mapper or SubjectMapper()

    def insert(self, subject: Subject) -> Subject:
        payload = self.mapper.to_persistence(subject)
        self.collection.insert_one(payload)
        return subject

    def update(self, subject: Subject) -> Optional[Subject]:
        payload = self.mapper.to_persistence(subject)
        _id = payload.pop("_id")

        result = self.collection.update_one(
            {"_id": _id},
            {"$set": payload},
        )
        if result.matched_count == 0:
            return None
        return subject

    def find_by_id(self, id: ObjectId) -> Optional[Subject]:
        doc = self.collection.find_one({"_id": id})
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def find_by_code(self, code: str) -> Optional[Subject]:
        doc = self.collection.find_one({"code": code})
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def find_by_name(self, name: str) -> Optional[Subject]:
        doc = self.collection.find_one({"name": name})
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def list_all(self, active_only: bool = False) -> list[Subject]:
        query: dict = {}
        if active_only:
            query["is_active"] = True

        cursor = self.collection.find(query)
        return [self.mapper.to_domain(doc) for doc in cursor]