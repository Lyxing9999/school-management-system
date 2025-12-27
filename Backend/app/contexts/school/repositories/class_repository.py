from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.mapper.class_mapper import ClassSectionMapper
from app.contexts.shared.lifecycle.updates import now_utc
from pymongo import ReturnDocument

class IClassSectionRepository(ABC):
    @abstractmethod
    def insert(self, section: ClassSection, *, session=None) -> ClassSection: ...

    @abstractmethod
    def update(self, section: ClassSection, *, session=None) -> bool: ...

    @abstractmethod
    def find_by_id(self, id: ObjectId, *, session=None) -> Optional[ClassSection]: ...

    @abstractmethod
    def find_by_name(self, name: str, *, session=None) -> Optional[ClassSection]: ...

    @abstractmethod
    def set_teacher(self, class_id: ObjectId, teacher_id: ObjectId | None, *, session=None) -> bool: ...

    @abstractmethod
    def try_increment_enrollment(self, class_id: ObjectId, *, session=None) -> Optional[ClassSection]: ...

    @abstractmethod
    def try_decrement_enrollment(self, class_id: ObjectId, *, session=None) -> Optional[ClassSection]: ...




class MongoClassSectionRepository(IClassSectionRepository):
    """
    MongoDB implementation of IClassSectionRepository.

    - Uses ClassSectionMapper to go domain <-> Mongo dict
    """

    def __init__(
        self,
        collection: Collection,
        mapper: ClassSectionMapper | None = None,
    ):
        self.collection = collection
        self.mapper = mapper or ClassSectionMapper()




    def start_session(self):
        return self.collection.database.client.start_session()
    # ---------- Write methods ----------



    def insert(self, section: ClassSection) -> ClassSection:
        payload = self.mapper.to_persistence(section)
        self.collection.insert_one(payload)
        return section

    def update(self, section: ClassSection) -> bool:
        payload = self.mapper.to_persistence(section)
        _id = payload.pop("_id")

        result = self.collection.update_one({"_id": _id}, {"$set": payload})
        return result.matched_count > 0
    # ---------- Read methods ----------

    def find_by_id(self, id: ObjectId, *, session=None) -> Optional[ClassSection]:
        doc = self.collection.find_one({"_id": id}, session=session)
        return None if not doc else self.mapper.to_domain(doc)

    def find_by_name(self, name: str) -> Optional[ClassSection]:
        doc = self.collection.find_one(
            {"name": name}
        )
        if not doc:
            return None
        return self.mapper.to_domain(doc)

    def set_teacher(self, class_id: ObjectId, teacher_id: Optional[ObjectId], *, session=None) -> bool:
        res = self.collection.update_one(
            {"_id": class_id, "lifecycle.deleted_at": None},
            {"$set": {"teacher_id": teacher_id, "lifecycle.updated_at": now_utc()}},
            session=session,
        )
        return res.matched_count == 1




    def try_increment_enrollment(self, class_id: ObjectId, *, session=None) -> Optional[ClassSection]:
        doc = self.collection.find_one_and_update(
            {
                "_id": class_id,
                "lifecycle.deleted_at": None,
                "status": "active",
                "$expr": {"$lt": ["$enrolled_count", "$max_students"]},
            },
            {"$inc": {"enrolled_count": 1}, "$set": {"lifecycle.updated_at": now_utc()}},
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        return None if not doc else self.mapper.to_domain(doc)

    def try_decrement_enrollment(self, class_id: ObjectId, *, session=None) -> Optional[ClassSection]:
        doc = self.collection.find_one_and_update(
            {
                "_id": class_id,
                "lifecycle.deleted_at": None,
                "$expr": {"$gt": ["$enrolled_count", 0]},
            },
            {"$inc": {"enrolled_count": -1}, "$set": {"lifecycle.updated_at": now_utc()}},
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        return None if not doc else self.mapper.to_domain(doc)