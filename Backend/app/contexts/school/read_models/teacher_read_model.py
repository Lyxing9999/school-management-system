
from typing import Optional, Union

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import not_deleted
from app.contexts.shared.model_converter import mongo_converter


class TeacherReadModel:
    """
    Read model for teacher-related queries used by ClassFactory:
    - How many classes is this teacher currently assigned to?
    - What is their max class load?
    """

    def __init__(self, db: Database):
        self.classes: Collection = db["classes"]
        self.teachers: Collection = db["teachers"]

    def _oid(self, v: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(v)

    def count_classes_for_teacher(self, teacher_id: Union[str, ObjectId]) -> int:
        """
        Count non-deleted classes where this teacher is the assigned teacher.
        """
        tid = self._oid(teacher_id)
        return self.classes.count_documents(not_deleted({"teacher_id": tid}))

    def get_max_class_load(self, teacher_id: Union[str, ObjectId]) -> Optional[int]:
        """
        Return the teacher's max class load if stored, or None if not configured.
        """
        tid = self._oid(teacher_id)
        doc = self.teachers.find_one(not_deleted({"_id": tid}))
        if not doc:
            return None
        value = doc.get("max_class_load")
        return int(value) if value is not None else None