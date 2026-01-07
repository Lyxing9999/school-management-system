from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.results import UpdateResult

from app.contexts.shared.lifecycle.filters import not_deleted
from app.contexts.shared.lifecycle.updates import now_utc

from ..domain.student import Student
from ..errors.student_exceptions import StudentUpdateFailedException
from ..mapper.student_mapper import StudentMapper


class MongoStudentRepository:
    def __init__(self, collection: Collection):
        self.collection = collection
        self._mapper = StudentMapper()

    def insert(self, student: Student) -> Student:
        payload = self._mapper.to_persistence(student)
        result = self.collection.insert_one(payload)
        student.id = result.inserted_id
        return student

    def find_by_id(self, id: ObjectId) -> Optional[Student]:
        doc = self.collection.find_one(not_deleted({"_id": id}))
        return self._mapper.to_domain(doc) if doc else None

    def find_by_user_id(self, user_id: ObjectId) -> Optional[Student]:
        doc = self.collection.find_one(not_deleted({"user_id": user_id}))
        return self._mapper.to_domain(doc) if doc else None

    def update(self, student: Student) -> Student:
        payload = self._mapper.to_persistence(student)
        _id = payload.pop("_id")

        result: UpdateResult = self.collection.update_one(
            not_deleted({"_id": _id}),
            {"$set": payload},
        )

        if result.matched_count == 0:
            raise StudentUpdateFailedException(
                user_id=student.user_id,
                student_id=student.id,
                reason="Student not found or deleted",
            )

        return student

    def try_join_class(self, student_id: ObjectId, class_id: ObjectId, *, session=None) -> bool:
        """
        IMPORTANT: enforce business status active at DB level (prevents bypassing domain rule)
        """
        res = self.collection.update_one(
            not_deleted({"_id": student_id, "current_class_id": None, "status": "active"}),
            {"$set": {"current_class_id": class_id, "lifecycle.updated_at": now_utc()}},
            session=session,
        )
        return res.modified_count == 1

    def try_leave_class(self, student_id: ObjectId, class_id: ObjectId, *, session=None) -> bool:
        """
        Leaving can be allowed even if status != active (cleanup). Keep only not_deleted.
        """
        res = self.collection.update_one(
            not_deleted({"_id": student_id, "current_class_id": class_id}),
            {"$set": {"current_class_id": None, "lifecycle.updated_at": now_utc()}},
            session=session,
        )
        return res.modified_count == 1

    def revert_join(self, student_id: ObjectId, class_id: ObjectId, *, session=None) -> None:
        """
        Rollback helper — should not require status active.
        """
        self.collection.update_one(
            not_deleted({"_id": student_id, "current_class_id": class_id}),
            {"$set": {"current_class_id": None, "lifecycle.updated_at": now_utc()}},
            session=session,
        )