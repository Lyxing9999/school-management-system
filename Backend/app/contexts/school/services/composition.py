from pymongo.database import Database

from app.contexts.school.services.use_cases import (
    ClassService,
    EnrollmentService,
    SubjectService,
    ScheduleService,
    AttendanceService,
    GradeService,
    ClassRelationsService
)

from app.contexts.school.repositories import (
    MongoClassSectionRepository,
    MongoAttendanceRepository,
    MongoGradeRepository,
    MongoSubjectRepository,
    MongoScheduleRepository,
)

from app.contexts.school.mapper import (
    ClassSectionMapper,
    AttendanceMapper,
    GradeMapper,
    SubjectMapper,
    ScheduleMapper,
)

from app.contexts.school.services.lifecycle import (
    ClassLifecycleService,
    SubjectLifecycleService,
    ScheduleLifecycleService,
    GradeLifecycleService,
    AttendanceLifecycleService,
)
from app.contexts.school.ports import SchedulePort, StudentMembershipPort
from app.contexts.student.services.student_service import StudentService

from app.contexts.student.adapters.mongo_student_membership_gateway import MongoStudentMembershipGateway
from app.contexts.school.adapters.mongo_schedule_gateway import MongoScheduleGateway

from app.contexts.school.policies import (
    SubjectUpdatePolicy,
    GradePolicy,
    AttendancePolicy,
)

from app.contexts.school.composition import build_school_factories
from app.contexts.school.services.facade import SchoolFacade


def build_school_facade(db: Database) -> SchoolFacade:
    class_factory, attendance_factory, grade_factory, subject_factory = build_school_factories(db)

    class_repo = MongoClassSectionRepository(db["classes"], ClassSectionMapper())
    attendance_repo = MongoAttendanceRepository(db["attendance"], AttendanceMapper())
    grade_repo = MongoGradeRepository(db["grades"], GradeMapper())
    subject_repo = MongoSubjectRepository(db["subjects"], SubjectMapper())
    schedule_repo = MongoScheduleRepository(db["schedules"], ScheduleMapper())

    student_membership: StudentMembershipPort = MongoStudentMembershipGateway(db)
    schedule: SchedulePort = MongoScheduleGateway(db)

    class_lifecycle = ClassLifecycleService(db)
    subject_lifecycle = SubjectLifecycleService(db)
    schedule_lifecycle = ScheduleLifecycleService(db)
    grade_lifecycle = GradeLifecycleService(db)
    attendance_lifecycle = AttendanceLifecycleService(db)

    grade_policy = GradePolicy(db)
    attendance_policy = AttendancePolicy(db)
    subject_update_policy = SubjectUpdatePolicy(db)

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
        subject_update_policy=subject_update_policy,
    )

    schedule_service = ScheduleService(
        schedule_repo=schedule_repo,
        class_repo=class_repo,
        schedule_lifecycle=schedule_lifecycle,
    )

    attendance_service = AttendanceService(
        attendance_factory=attendance_factory,
        attendance_repo=attendance_repo,
        attendance_policy=attendance_policy,
        attendance_lifecycle=attendance_lifecycle,
    )

    grade_service = GradeService(
        grade_factory=grade_factory,
        grade_repo=grade_repo,
        grade_policy=grade_policy,
        grade_lifecycle=grade_lifecycle,
    )


    class_relations_service = ClassRelationsService(
        class_repo=class_repo,
        student_membership=student_membership,
        schedule=schedule,
    )

    return SchoolFacade(
        class_service=class_service,
        enrollment_service=enrollment_service,
        subject_service=subject_service,
        schedule_service=schedule_service,
        attendance_service=attendance_service,
        grade_service=grade_service,
        class_relations_service=class_relations_service,
    )