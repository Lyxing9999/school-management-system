# app/contexts/school/services/composition.py
from pymongo.database import Database

from app.contexts.school.services.facade import SchoolFacade

from app.contexts.school.services.use_cases.class_service import ClassService
from app.contexts.school.services.use_cases.enrollment_service import EnrollmentService
from app.contexts.school.services.use_cases.subject_service import SubjectService
from app.contexts.school.services.use_cases.schedule_service import ScheduleService
from app.contexts.school.services.use_cases.attendance_service import AttendanceService
from app.contexts.school.services.use_cases.grade_service import GradeService
from app.contexts.school.services.use_cases.teacher_assignment_service import TeacherAssignmentService

from app.contexts.school.composition import build_school_factories

from app.contexts.school.repositories.class_repository import MongoClassSectionRepository
from app.contexts.school.repositories.attendance_repository import MongoAttendanceRepository
from app.contexts.school.repositories.grade_repository import MongoGradeRepository
from app.contexts.school.repositories.subject_repository import MongoSubjectRepository
from app.contexts.school.repositories.schedule_repository import MongoScheduleRepository
from app.contexts.school.repositories.teacher_assignment_repository import TeacherAssignmentRepository

from app.contexts.school.mapper.class_mapper import ClassSectionMapper
from app.contexts.school.mapper.attendance_mapper import AttendanceMapper
from app.contexts.school.mapper.grade_mapper import GradeMapper
from app.contexts.school.mapper.subject_mapper import SubjectMapper
from app.contexts.school.mapper.schedule_mapper import ScheduleMapper

from app.contexts.school.services.lifecycle.class_lifecycle_service import ClassLifecycleService
from app.contexts.school.services.lifecycle.subject_lifecycle_service import SubjectLifecycleService
from app.contexts.school.services.lifecycle.schedule_lifecycle_service import ScheduleLifecycleService

from app.contexts.student.services.student_service import StudentService

def build_school_facade(db: Database) -> SchoolFacade:
    class_factory, attendance_factory, grade_factory, subject_factory = build_school_factories(db)

    class_repo = MongoClassSectionRepository(db["classes"], ClassSectionMapper())
    attendance_repo = MongoAttendanceRepository(db["attendance"], AttendanceMapper())
    grade_repo = MongoGradeRepository(db["grades"], GradeMapper())
    subject_repo = MongoSubjectRepository(db["subjects"], SubjectMapper())
    schedule_repo = MongoScheduleRepository(db["schedules"], ScheduleMapper())
    teacher_assignment_repo = TeacherAssignmentRepository(db["teacher_subject_assignments"])

    class_lifecycle = ClassLifecycleService(db)
    subject_lifecycle = SubjectLifecycleService(db)
    schedule_lifecycle = ScheduleLifecycleService(db)


    class_service = ClassService(
        class_factory=class_factory,
        class_repo=class_repo,
        class_lifecycle=class_lifecycle,
    )

    student_service = StudentService(db)

    enrollment_service = EnrollmentService(
        class_repo=class_repo,
        student_service_getter=lambda: student_service,
    )

    subject_service = SubjectService(
        subject_factory=subject_factory,
        subject_repo=subject_repo,
        subject_lifecycle=subject_lifecycle,
    )

    schedule_service = ScheduleService(
        schedule_repo=schedule_repo,
        class_repo=class_repo,
        schedule_lifecycle=schedule_lifecycle,
    )

    attendance_service = AttendanceService(
        attendance_factory=attendance_factory,
        attendance_repo=attendance_repo,
    )

    grade_service = GradeService(
        grade_factory=grade_factory,
        grade_repo=grade_repo,
    )

    teacher_assignment_service = TeacherAssignmentService(
        teacher_assignment_repo=teacher_assignment_repo,
        class_repo=class_repo,
        subject_repo=subject_repo,
    )

    return SchoolFacade(
        class_service=class_service,
        enrollment_service=enrollment_service,
        subject_service=subject_service,
        schedule_service=schedule_service,
        attendance_service=attendance_service,
        grade_service=grade_service,
        teacher_assignment_service=teacher_assignment_service,
    )