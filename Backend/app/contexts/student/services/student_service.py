from __future__ import annotations
from typing import List
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
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

    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def get_my_attendance(self, student_user_id: str | ObjectId) -> list[dict]:
        sid = self._oid(student_user_id)
        # Use read model directly for summaries
        return self.attendance_read.list_by_student(sid)

    def get_my_grades(self, student_user_id: str | ObjectId) -> list[dict]:
        sid = self._oid(student_user_id)
        return self.grade_read.list_by_student(sid)

    def get_my_schedule(self, student_user_id: str | ObjectId) -> list[dict]:
        sid = self._oid(student_user_id)
        return self.schedule_read.list_for_student(sid)



    # later: compute GPA in this service using GradeReadModel