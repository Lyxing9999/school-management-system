# app/contexts/school/repository/class_repository.py

from typing import Optional, Iterable
from pymongo.database import Database
from bson import ObjectId

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.mapper.class_mapper import ClassSectionMapper
from app.contexts.shared.model_converter import mongo_converter


class ClassRepository:
    def __init__(self, db: Database):
        self.collection = db.class_sections
        self.mapper = ClassSectionMapper()

    def save(self, cls: ClassSection) -> ClassSection:
        doc = self.mapper.to_persistence(cls)
        self.collection.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
        return cls

    def find_by_id(self, class_id: str | ObjectId) -> Optional[ClassSection]:
        object_id = mongo_converter.convert_to_object_id(class_id)
        doc = self.collection.find_one({"_id": object_id, "deleted": False})
        return self.mapper.to_domain(doc) if doc else None

    def find_by_teacher(self, teacher_id: ObjectId) -> Iterable[ClassSection]:
        cursor = self.collection.find({"teacher_id": teacher_id, "deleted": False})
        for doc in cursor:
            yield self.mapper.to_domain(doc)