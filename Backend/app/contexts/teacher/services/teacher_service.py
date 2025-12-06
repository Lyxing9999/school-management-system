from __future__ import annotations
from typing import List, Union, Dict, Any
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService


from app.contexts.teacher.data_transfer.requests import (
    TeacherMarkAttendanceRequest,
    TeacherChangeAttendanceStatusRequest,
    TeacherAddGradeRequest,
    TeacherUpdateGradeScoreRequest,
    TeacherChangeGradeTypeRequest,
)
from app.contexts.school.data_transfer.responses import (
    attendance_to_dto,
    grade_to_dto,
    AttendanceDTO,
    GradeDTO,
)
from app.contexts.teacher.read_models.teacher_read_models import TeacherReadModel
from app.contexts.teacher.error.teacher_exceptions import TeacherForbiddenException
from app.contexts.shared.model_converter import mongo_converter

class TeacherService:
    """
    Application service for teacher-facing use cases.
    Uses SchoolService as the domain façade.
    """

    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        self._teacher_read = TeacherReadModel(db)

    @property
    def teacher_read(self) -> TeacherReadModel:
        return self._teacher_read

    # ---------- Classes ----------

    def list_my_classes_enriched(self, teacher_id: str | ObjectId) -> list[dict]:
        return self.teacher_read.list_my_classes_enriched(teacher_id)
        


    # ---------- Attendance ----------

    def mark_attendance(
        self,
        teacher_id: str | ObjectId,
        payload: TeacherMarkAttendanceRequest,
    ) -> AttendanceDTO:
        record = self.school_service.mark_attendance(
            student_id=payload.student_id,
            class_id=payload.class_id,
            status=payload.status,
            teacher_id=teacher_id,
            record_date=payload.record_date,
        )
        return attendance_to_dto(record)

    def change_attendance_status(
        self,
        teacher_id: str | ObjectId,
        attendance_id: str | ObjectId,
        payload: TeacherChangeAttendanceStatusRequest,
    ) -> AttendanceDTO:
        # biz rule "only assigned teacher can modify" is enforced in domain/factory/extra checks
        record = self.school_service.change_attendance_status(
            attendance_id=attendance_id,
            new_status=payload.new_status,
        )
        if record is None:
            return None  # route will convert to 404 or similar
        return attendance_to_dto(record)

    def list_attendance_for_class_enriched(
        self,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId,
    ) -> list[dict]:
        docs = self.teacher_read.list_attendance_for_class_enriched(class_id)
        return docs

    # ---------- Grades ----------

    def add_grade(
        self,
        teacher_id: str | ObjectId,
        payload: TeacherAddGradeRequest,
    ) -> GradeDTO:
        grade = self.school_service.add_grade(
            student_id=payload.student_id,
            subject_id=payload.subject_id,
            score=payload.score,
            type=payload.type,
            teacher_id=teacher_id,
            class_id=payload.class_id,
            term=payload.term,
        )
        return grade_to_dto(grade)

    def update_grade_score(
        self,
        teacher_id: str | ObjectId,
        grade_id: str | ObjectId,
        payload: TeacherUpdateGradeScoreRequest,
    ) -> GradeDTO | None:
        grade = self.school_service.update_grade_score(
            grade_id=grade_id,
            new_score=payload.score,
        )
        if grade is None:
            return None
        return grade_to_dto(grade)

    def change_grade_type(
        self,
        teacher_id: str | ObjectId,
        grade_id: str | ObjectId,
        payload: TeacherChangeGradeTypeRequest,
    ) -> GradeDTO | None:
        grade = self.school_service.change_grade_type(
            grade_id=grade_id,
            new_type=payload.type,
        )
        if grade is None:
            return None
        return grade_to_dto(grade)

    def list_grades_for_class_enriched(
        self,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId,
    ) -> list[GradeDTO]:
        return self.teacher_read.list_grades_for_class_enriched(class_id)




    def list_class_name_options_for_teacher(
        self,
        teacher_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        return self.teacher_read.list_class_name_options_for_teacher(teacher_id)



    def list_student_name_options_in_class(
        self,
        class_id: Union[str, ObjectId],
        teacher_id: Union[str, ObjectId]
    ) -> List[Dict]:
        cls = self.teacher_read.classes.get_by_id(class_id)
        if not cls or cls.get("teacher_id") != mongo_converter.convert_to_object_id(teacher_id):
            raise TeacherForbiddenException()

        return self.teacher_read.list_student_name_options_in_class(class_id)

    def list_subject_name_options_in_class(
        self,
        class_id: Union[str, ObjectId],
        teacher_id: Union[str, ObjectId]
    ) -> List[Dict]:
        cls = self.teacher_read.classes.get_by_id(class_id)
        if not cls or cls.get("teacher_id") != mongo_converter.convert_to_object_id(teacher_id):
            raise TeacherForbiddenException()

        return self.teacher_read.list_subject_name_options_in_class(class_id)


    def list_my_schedule_enriched(self, teacher_id: Union[str, ObjectId]) -> List[Dict]:
        return self.teacher_read.list_schedule_for_teacher_enriched(teacher_id)