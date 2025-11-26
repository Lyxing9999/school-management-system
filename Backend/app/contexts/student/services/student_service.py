from __future__ import annotations
from typing import List
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.data_transfer.responses import (
    ClassSectionDTO,
    AttendanceDTO,
    GradeDTO,
    ScheduleDTO,
)
from app.contexts.shared.model_converter import mongo_converter


class StudentService:
    """
    Student-facing application service.
    Used for 'me' endpoints: my schedule, my attendance, my grades.
    """

    def __init__(self, db: Database, school_service: SchoolService):
        self.db = db
        self.school_service = school_service

        self.attendance_read = AttendanceReadModel(db)
        self.grade_read = GradeReadModel(db)
        self.schedule_read = ScheduleReadModel(db)
        self.class_read = ClassReadModel(db)

    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    # ---------------- ATTENDANCE ----------------

    def get_my_attendance(
        self,
        student_id: str | ObjectId,
        class_id: str | ObjectId | None = None,
    ) -> list[AttendanceDTO]:
        sid = self._oid(student_id)

        # If your read model only supports (student, class) you can simplify
        if class_id is not None:
            cid = self._oid(class_id)
            docs = self.attendance_read.list_student_attendances(sid, cid)
        else:
            # implement this in your read model or adjust
            docs = self.attendance_read.list_student_attendances(sid)

        return mongo_converter.list_to_dto(docs, AttendanceDTO)

    # ---------------- GRADES ----------------

    def get_my_grades(
        self,
        student_id: str | ObjectId,
        term: str | None = None,
    ) -> list[GradeDTO]:
        sid = self._oid(student_id)

        # If later you add filtering by term, plug it in here
        # e.g. self.grade_read.list_student_grades_by_term(sid, term)
        docs = self.grade_read.list_student_grades(sid)

        return mongo_converter.list_to_dto(docs, GradeDTO)

    # ---------------- SCHEDULE ----------------

    def get_my_schedule(
        self,
        student_id: str | ObjectId,
    ) -> list[ScheduleDTO]:
        sid = self._oid(student_id)
        docs = self.schedule_read.list_student_schedules(sid)
        return mongo_converter.list_to_dto(docs, ScheduleDTO)

    # ---------------- CLASSES ----------------

    def get_my_classes(
        self,
        student_id: str | ObjectId,
    ) -> list[ClassSectionDTO]:
        sid = self._oid(student_id)
        docs = self.class_read.list_student_classes(sid)
        return mongo_converter.list_to_dto(docs, ClassSectionDTO)