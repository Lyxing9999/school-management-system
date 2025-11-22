# app/contexts/teacher/services/teacher_service.py
from __future__ import annotations
from typing import List
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel

from app.contexts.teacher.data_transfer.requests import (
    TeacherMarkAttendanceRequest,
    TeacherChangeAttendanceStatusRequest,
    TeacherAddGradeRequest,
    TeacherUpdateGradeScoreRequest,
    TeacherChangeGradeTypeRequest,
)
from app.contexts.school.data_transfer.responses import (
    class_section_to_dto,
    attendance_to_dto,
    grade_to_dto,
    ClassSectionDTO,
    AttendanceDTO,
    GradeDTO,
)


class TeacherService:
    """
    Application service for teacher-facing use cases.
    Uses SchoolService as the domain façade.
    """

    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        # read models for teacher-specific queries
        self.class_read = ClassReadModel(db)
        self.attendance_read = AttendanceReadModel(db)
        self.grade_read = GradeReadModel(db)

    # ---------- Classes ----------

    def get_my_classes(self, teacher_id: str | ObjectId) -> list[ClassSectionDTO]:
        docs = self.class_read.list_by_teacher(teacher_id)
        # docs are raw dicts; you may want a tiny mapper or just adapt:
        result: list[ClassSectionDTO] = []
        for d in docs:
            section = self.school_service.class_repo.mapper.to_domain(d)
            result.append(class_section_to_dto(section))
        return result

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

    def list_attendance_for_class(
        self,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId,
    ) -> list[AttendanceDTO]:
        # you *could* enforce that class.teacher_id == teacher_id using read-model here
        docs = self.attendance_read.list_by_class(class_id)
        records: list[AttendanceDTO] = []
        for d in docs:
            record = self.school_service.attendance_repo.mapper.to_domain(d)
            records.append(attendance_to_dto(record))
        return records

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

    def list_grades_for_class(
        self,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId,
    ) -> list[GradeDTO]:
        docs = self.grade_read.list_by_class(class_id)
        grades: list[GradeDTO] = []
        for d in docs:
            g = self.school_service.grade_repo.mapper.to_domain(d)
            grades.append(grade_to_dto(g))
        return grades