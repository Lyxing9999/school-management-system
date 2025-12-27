from __future__ import annotations

from typing import Optional
from bson import ObjectId
from pymongo.database import Database

from app.contexts.student.repositories.student_repository import MongoStudentRepository
from app.contexts.student.read_models.student_read_model import StudentReadModel


class MongoStudentMembershipGateway:
    def __init__(self, db: Database):
        self._repo = MongoStudentRepository(db["students"])
        self._read = StudentReadModel(db)

    def list_student_ids_in_class(self, class_id: ObjectId, *, session=None) -> set[ObjectId]:
        return self._read.list_student_ids_in_class(class_id, session=session)

    def exists(self, student_id: ObjectId, *, session=None) -> bool:
        return self._read.exists(student_id, session=session)

    def get_current_class_id(self, student_id: ObjectId, *, session=None) -> Optional[ObjectId]:
        return self._read.get_current_class_id(student_id, session=session)

    def try_join_class(self, student_id: ObjectId, class_id: ObjectId, *, session=None) -> bool:
        return self._repo.try_join_class(student_id, class_id, session=session)

    def try_leave_class(self, student_id: ObjectId, class_id: ObjectId, *, session=None) -> bool:
        return self._repo.try_leave_class(student_id, class_id, session=session)

    def revert_join(self, student_id: ObjectId, class_id: ObjectId, *, session=None) -> None:
        self._repo.revert_join(student_id, class_id, session=session)