from __future__ import annotations
from typing import List
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.data_transfer.responses import (
    ClassSectionDTO,
    AttendanceDTO,
    GradeDTO,
)
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.student.data_transfer.responses import StudentScheduleDTO
from app.contexts.student.read_models.student_read_model import StudentReadModel

class StudentService:
    """
    Student-facing application service.
    Used for 'me' endpoints: my schedule, my attendance, my grades.
    """

    def __init__(self, db: Database, school_service: SchoolService):
        self.db = db
        self.school_service = school_service
        self._student_read: StudentReadModel | None = None

    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)


    @property
    def student_read(self) -> StudentReadModel:
        if self._student_read is None:
            self._student_read = StudentReadModel(self.db)
        return self._student_read

    # ---------------- ATTENDANCE ----------------



    def get_my_attendance(
        self,
        student_id: str | ObjectId,
        class_id: str | ObjectId | None = None,
    ) -> list[AttendanceDTO]:
        sid = self._oid(student_id)
        cid = self._oid(class_id)
        return self.student_read.list_my_attendance(sid, cid)
    # ---------------- GRADES ----------------

    def get_my_grades(
        self,
        student_id: str | ObjectId,
        term: str | None = None,
    ) -> list[GradeDTO]:
        sid = self._oid(student_id)

            # If later you add filtering by term, plug it in here
            # e.g. self.grade_read.list_student_grades_by_term(sid, term)
        return self.student_read.list_my_grades_enriched(sid)



    # ---------------- SCHEDULE ----------------

    def get_my_schedule(
        self,
        student_id: str | ObjectId,
    ) -> list[StudentScheduleDTO]:
        sid = self._oid(student_id)
        return self.student_read.list_my_schedule(sid)
        

    # ---------------- CLASSES ----------------

    def get_my_classes(
        self,
        student_id: str | ObjectId,
    ) -> list[ClassSectionDTO]:
        sid = self._oid(student_id)
        return self.student_read.list_my_classes_enriched(sid)
        