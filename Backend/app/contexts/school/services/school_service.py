from __future__ import annotations
from typing import Iterable, List, Optional, TYPE_CHECKING

from bson import ObjectId
from datetime import date as date_type


from pymongo.database import Database

from app.contexts.school.composition import build_school_factories
from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.domain.schedule import ScheduleSlot, DayOfWeek
from app.contexts.school.domain.subject import Subject

from app.contexts.school.repositories.class_repository import MongoClassSectionRepository
from app.contexts.school.repositories.attendance_repository import MongoAttendanceRepository
from app.contexts.school.repositories.grade_repository import MongoGradeRepository
from app.contexts.school.repositories.subject_repository import MongoSubjectRepository
from app.contexts.school.repositories.schedule_repository import MongoScheduleRepository

from app.contexts.school.mapper.class_mapper import ClassSectionMapper
from app.contexts.school.mapper.attendance_mapper import AttendanceMapper
from app.contexts.school.mapper.grade_mapper import GradeMapper
from app.contexts.school.mapper.subject_mapper import SubjectMapper
from app.contexts.school.mapper.schedule_mapper import ScheduleMapper


from app.contexts.shared.model_converter import mongo_converter

#domain exceptions
from app.contexts.school.errors.class_exceptions import ClassNotFoundException, StudentAlreadyEnrolledException
from app.contexts.school.errors.attendance_exceptions import AttendanceNotFoundException
from app.contexts.school.errors.grade_exceptions import GradeNotFoundException
from app.contexts.school.errors.subject_exceptions import SubjectNotFoundException
from app.contexts.school.errors.schedule_exceptions import ScheduleNotFoundException ,ScheduleUpdateFailedException
from app.contexts.student.errors.student_exceptions import StudentNotFoundException


if TYPE_CHECKING:
    from app.contexts.student.services.student_service import StudentService


class SchoolService:
    def __init__(self, db: Database):
        # 1) Factories
        (
            self.class_factory,
            self.attendance_factory,
            self.grade_factory,
            self.subject_factory
        ) = build_school_factories(db)

        self.db = db
        # 2) Repositories
        self.class_repo = MongoClassSectionRepository(db["classes"], ClassSectionMapper())
        self.attendance_repo = MongoAttendanceRepository(db["attendance"], AttendanceMapper())
        self.grade_repo = MongoGradeRepository(db["grades"], GradeMapper())
        self.subject_repo = MongoSubjectRepository(db["subjects"], SubjectMapper())
        self.schedule_repo = MongoScheduleRepository(db["schedule"], ScheduleMapper())
        
    @property
    def _student_service(self) -> StudentService:
        from app.contexts.student.services.student_service import StudentService

        return StudentService(self.db)
    def create_class(
            self,
            name: str,
            teacher_id: str | ObjectId | None = None,
            subject_ids: Iterable[str | ObjectId] | None = None,
            max_students: int | None = None,
        ) -> ClassSection:
            """
            Admin / School use case:
            - Validate via ClassFactory (name uniqueness, teacher load)
            - Persist via MongoClassSectionRepository
            """
            section = self.class_factory.create_class(
                name=name,
                teacher_id=teacher_id,
                subject_ids=subject_ids,
                max_students=max_students,
            )
            return self.class_repo.insert(section)

    def enroll_student_to_class(
        self,
        class_id: str | ObjectId,
        student_id: str | ObjectId,
    ) -> Optional[ClassSection]:
            
        class_oid = mongo_converter.convert_to_object_id(class_id)
        student_oid = mongo_converter.convert_to_object_id(student_id)

        section = self.class_repo.find_by_id(class_oid)
        if section is None:
            raise ClassNotFoundException(class_id)
        student = self._student_service.get_student_by_id(student_oid)
        if student is None:
            raise StudentNotFoundException(student_id)
        if student.current_class_id is not None:
            raise StudentAlreadyEnrolledException(
                student_id=student_oid,
                current_class_id=student.current_class_id,
                target_class_id=class_oid
            )
        section.increment_enrollment()
        self.class_repo.update(section)
        try:
            self._student_service.join_class(class_id=class_oid, student_id=student_oid)
        except Exception as e:
            section.decrement_enrollment()
            self.class_repo.update(section)
            raise e

        return section

    def unenroll_student_from_class(
        self,
        class_id: str | ObjectId,
        student_id: str | ObjectId,
    ) -> Optional[ClassSection]:
        class_oid = mongo_converter.convert_to_object_id(class_id)
        student_oid = mongo_converter.convert_to_object_id(student_id)

        section = self.class_repo.find_by_id(class_oid)
        if section is None:
            raise ClassNotFoundException(class_id)

        section.decrement_enrollment()
        self.class_repo.update(section)

        self._student_service.leave_class(student_id=student_oid)
        
        return section
    # ============================================================
    # Attendance use cases
    # ============================================================

    def mark_attendance(
        self,
        student_id: str | ObjectId,
        class_id: str | ObjectId,
        status: AttendanceStatus | str,
        teacher_id: str | ObjectId,
        record_date: date_type | None = None,
    ) -> AttendanceRecord:
        """
        Teacher use case:
        1. AttendanceFactory:
           - validates teacher is class teacher
           - validates student is enrolled
           - prevents duplicate record for same date
           - validates status via domain
        2. Persist AttendanceRecord via repo.
        """
        record = self.attendance_factory.create_record(
            student_id=student_id,
            class_id=class_id,
            status=status,
            teacher_id=teacher_id,
            record_date=record_date,
        )
        return self.attendance_repo.insert(record)

    def change_attendance_status(
        self,
        attendance_id: str | ObjectId,
        new_status: AttendanceStatus | str,
    ) -> Optional[AttendanceRecord]:
        """
        Simple example of loading a record, using domain behavior,
        then saving it back.
        """
        oid = mongo_converter.convert_to_object_id(attendance_id)
        existing = self.attendance_repo.find_by_id(oid)
        if existing is None:
            raise AttendanceNotFoundException(attendance_id)

        existing.change_status(new_status)
        return self.attendance_repo.update(existing)

    def get_attendance_by_id(
        self, attendance_id: str | ObjectId
    ) -> Optional[AttendanceRecord]:
        oid = mongo_converter.convert_to_object_id(attendance_id)
        return self.attendance_repo.find_by_id(oid)

    # ============================================================
    # Grade / Grading use cases
    # ============================================================

    def add_grade(
        self,
        student_id: str | ObjectId,
        subject_id: str | ObjectId,
        score: float,
        type: GradeType | str,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId | None = None,
        term: str | None = None,
    ) -> GradeRecord:
        """
        Teacher use case:
        1. GradeFactory:
           - validates subject exists
           - validates class exists (if given)
           - validates teacher can grade this subject/class
           - validates student is enrolled for subject/class
        2. GradeRecord:
           - validates score (0–100)
           - validates type (exam/assignment)
        3. Persist via MongoGradeRepository.
        """
        grade = self.grade_factory.create_grade(
            student_id=student_id,
            subject_id=subject_id,
            score=score,
            type=type,
            teacher_id=teacher_id,
            class_id=class_id,
            term=term,
        )
        return self.grade_repo.insert(grade)

    def update_grade_score(
        self,
        grade_id: str | ObjectId,
        new_score: float,
    ) -> Optional[GradeRecord]:
        """
        Load grade aggregate, use domain rule to update score, then persist.
        """
        oid = mongo_converter.convert_to_object_id(grade_id)
        existing = self.grade_repo.find_by_id(oid)
        if existing is None:
            raise GradeNotFoundException(grade_id)

        existing.set_score(new_score)
        return self.grade_repo.update(existing)

    def change_grade_type(
        self,
        grade_id: str | ObjectId,
        new_type: GradeType | str,
    ) -> Optional[GradeRecord]:
        """
        Will raise GradeTypeChangeForbiddenException if score already set.
        """
        oid = mongo_converter.convert_to_object_id(grade_id)
        existing = self.grade_repo.find_by_id(oid)
        if existing is None:
            raise GradeNotFoundException(grade_id)

        existing.change_type(new_type)
        return self.grade_repo.update(existing)

    def get_grade_by_id(
        self, grade_id: str | ObjectId
    ) -> Optional[GradeRecord]:
        oid = mongo_converter.convert_to_object_id(grade_id)
        return self.grade_repo.find_by_id(oid)

    # ===========================
    # Subject use cases
    # ===========================

    def create_subject(
        self,
        name: str,
        code: str,
        description: str | None = None,
        allowed_grade_levels: Iterable[int] | None = None,
    ) -> Subject:
        subject = self.subject_factory.create_subject(
            name=name,
            code=code,
            description=description,
            allowed_grade_levels=allowed_grade_levels,
        )
        return self.subject_repo.insert(subject)


    def get_subject_by_id(self, subject_id: str | ObjectId) -> Subject | None:
        oid = mongo_converter.convert_to_object_id(subject_id)
        return self.subject_repo.find_by_id(oid)


    def get_subject_by_code(self, code: str) -> Subject | None:
        return self.subject_repo.find_by_code(code)

    def deactivate_subject(self, subject_id: str | ObjectId) -> Subject | None:
        oid = mongo_converter.convert_to_object_id(subject_id)
        subject = self.subject_repo.find_by_id(oid)
        if subject is None:
            raise SubjectNotFoundException(subject_id)
        subject.deactivate()
        return self.subject_repo.update(subject)

    def activate_subject(self, subject_id: str | ObjectId) -> Subject | None:
        oid = mongo_converter.convert_to_object_id(subject_id)
        subject = self.subject_repo.find_by_id(oid)
        if subject is None:
            raise SubjectNotFoundException(subject_id)
        subject.activate()
        return self.subject_repo.update(subject)

    # ============================================================
    # Schedule use cases
    # ============================================================

    def create_schedule_slot_for_class(
        self,
        class_id: str | ObjectId,
        teacher_id: str | ObjectId,
        day_of_week: DayOfWeek | int,
        start_time: time,
        end_time: time,
        room: str | None = None,
    ) -> ScheduleSlot:
        """
        Admin use case:
        - Create schedule slot for a class / teacher
        - Domain (ScheduleSlot) validates day/time and ordering
        - You can add conflict checks in a separate service/read model later
        """

        class_oid = mongo_converter.convert_to_object_id(class_id)
        teacher_oid = mongo_converter.convert_to_object_id(teacher_id)

        # Ensure class exists (good guard)
        section = self.class_repo.find_by_id(class_oid)
        if section is None:
            raise ClassNotFoundException(class_id)

        slot = ScheduleSlot(
            class_id=class_oid,
            teacher_id=teacher_oid,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            room=room,
        )
        return self.schedule_repo.insert(slot)

    def move_schedule_slot(
        self,
        slot_id: str | ObjectId,
        new_day_of_week: DayOfWeek | int,
        new_start_time: time,
        new_end_time: time,
        new_room: str | None = None,
    ) -> ScheduleSlot:
        """
        Admin use case:
        - Move existing schedule slot to a new day/time
        """
        oid = mongo_converter.convert_to_object_id(slot_id)
        slot = self.schedule_repo.find_by_id(oid)
        if slot is None:
            raise ScheduleNotFoundException(oid)

        slot.move(
            new_day_of_week=new_day_of_week,
            new_start=new_start_time,
            new_end=new_end_time,
            new_room=new_room
        )
        updated = self.schedule_repo.update(slot)
        if updated is None:
            raise ScheduleUpdateFailedException(slot_id)
        return updated

    def delete_schedule_slot(self, slot_id: str | ObjectId) -> bool:
        oid = mongo_converter.convert_to_object_id(slot_id)
        return self.schedule_repo.delete(oid)

