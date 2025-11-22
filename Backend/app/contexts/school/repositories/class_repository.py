from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.mapper.class_mapper import ClassSectionMapper


class IClassSectionRepository(ABC):
    """Interface for ClassSection repositories."""

    @abstractmethod
    def insert(self, section: ClassSection) -> ClassSection:
        ...

    @abstractmethod
    def update(self, section: ClassSection) -> Optional[ClassSection]:
        """
        Update an existing ClassSection.
        Returns:
            The updated ClassSection if a document was matched,
            or None if no document with that id exists.
        """
        ...

    @abstractmethod
    def find_by_id(self, id: ObjectId) -> Optional[ClassSection]:
        ...

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[ClassSection]:
        ...

    @abstractmethod
    def soft_delete(self, id: ObjectId) -> bool:
        ...




class MongoClassSectionRepository(IClassSectionRepository):
    """
    MongoDB implementation of IClassSectionRepository.

    - Uses ClassSectionMapper to go domain <-> Mongo dict
    - Respects `deleted` flag for soft delete
    """

    def __init__(
        self,
        collection: Collection,
        mapper: ClassSectionMapper | None = None,
    ):
        self.collection = collection
        self.mapper = mapper or ClassSectionMapper()

    # ---------- Write methods ----------

    def insert(self, section: ClassSection) -> ClassSection:
        payload = self.mapper.to_persistence(section)
        self.collection.insert_one(payload)
        return section

    def update(self, section: ClassSection) -> Optional[ClassSection]:
        payload = self.mapper.to_persistence(section)
        _id = payload.pop("_id")

        result = self.collection.update_one(
            {"_id": _id, "deleted": {"$ne": True}},
            {"$set": payload},
        )
        if result.matched_count == 0:
            return None
        return section

    def soft_delete(self, id: ObjectId) -> bool:
        result = self.collection.update_one(
            {"_id": id},
            {"$set": {"deleted": True}},
        )
        return result.matched_count == 1

    # ---------- Read methods ----------

    def find_by_id(self, id: ObjectId) -> Optional[ClassSection]:
        doc = self.collection.find_one(
            {"_id": id, "deleted": {"$ne": True}}
        )
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def find_by_name(self, name: str) -> Optional[ClassSection]:
        doc = self.collection.find_one(
            {"name": name, "deleted": {"$ne": True}}
        )
        if not doc:
            return None
        return self.mapper.to_domain(doc)

