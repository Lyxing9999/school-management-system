from __future__ import annotations
from typing import Final, Optional
from bson import ObjectId
from datetime import datetime
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.data_transfer.responses import (
    ClassSectionDTO,
    AttendanceDTO,
    GradeDTO,
)   
from app.contexts.shared.model_converter import mongo_converter


from ..data_transfer.responses import StudentScheduleDTO
from ..read_models.student_read_model import StudentReadModel
from ..repositories.student_repository import MongoStudentRepository
from ..domain.student import Student

class StudentService:
    """
    Student-facing application service.
    Used for 'me' endpoints: my schedule, my attendance, my grades.
    """

    def __init__(self, db: Database, school_service: SchoolService):
        self.db = db
        self.school_service = school_service
        self._student_read: Final(StudentReadModel | None) = None
        self._student_repo: Final(MongoStudentRepository | None) = None
    
    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)



    # ---------------- MY PROFILE ----------------
    
    def get_my_profile(self, user_id: str | ObjectId) -> Optional[Student]:
        uid = self._oid(user_id)
        return self._student_repo.find_by_user_id(uid)

    # ---------------- ATTENDANCE ----------------

    def get_my_attendance(
        self,
        student_id: str | ObjectId,
        class_id: str | ObjectId | None = None,
    ) -> list[AttendanceDTO]:
        sid = self._oid(student_id)
        cid = self._oid(class_id)
        return self._student_read.list_my_attendance_enriched(sid, cid)
    # ---------------- GRADES ----------------

    def get_my_grades(
        self,
        student_id: str | ObjectId,
        term: str | None = None,
    ) -> list[GradeDTO]:
        sid = self._oid(student_id)

        return self._student_read.list_my_grades_enriched(sid)



    # ---------------- SCHEDULE ----------------

    def get_my_schedule(
        self,
        student_id: str | ObjectId,
    ) -> list[StudentScheduleDTO]:
        sid = self._oid(student_id)
        return self._student_read.list_my_schedule_enriched(sid)
        

    # ---------------- CLASSES ----------------

    def get_my_classes(
        self,
        student_id: str | ObjectId,
    ) -> list[ClassSectionDTO]:
        sid = self._oid(student_id)
        return self._student_read.list_my_classes_enriched(sid)
        