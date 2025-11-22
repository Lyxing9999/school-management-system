from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.school.read_models.enrollment_read_model import EnrollmentReadModel
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.teacher_read_model import TeacherReadModel

from app.contexts.school.read_models.teacher_assignment_read_model import TeacherAssignmentReadModel

from app.contexts.school.factory.class_factory import ClassFactory
from app.contexts.school.factory.attendance_factory import AttendanceFactory
from app.contexts.school.factory.grade_factory import GradeFactory
from app.contexts.school.factory.subject_factory import SubjectFactory





def build_school_factories(db):
    class_read = ClassReadModel(db)
    subject_read_model = SubjectReadModel(db)
    enrollment_read = EnrollmentReadModel(db)
    attendance_read = AttendanceReadModel(db)
    teacher_read = TeacherReadModel(db)
    teacher_assignment_read = TeacherAssignmentReadModel(db)
    class_factory = ClassFactory(
        class_read_model=class_read,
        teacher_read_model=teacher_read,
    )

    attendance_factory = AttendanceFactory(
        class_read_model=class_read,
        enrollment_read_model=enrollment_read,
        attendance_read_model=attendance_read,
    )

    grade_factory = GradeFactory(
        class_read_model=class_read,
        subject_read_model=subject_read_model,
        enrollment_read_model=enrollment_read,
        teacher_assignment_read_model=teacher_assignment_read,
    )

    subject_factory = SubjectFactory(
        subject_read_model=subject_read_model,
    )

    return class_factory, attendance_factory, grade_factory, subject_factory