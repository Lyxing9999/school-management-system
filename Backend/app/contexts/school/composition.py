from app.contexts.school.read_models import (
    ClassReadModel,
    SubjectReadModel,
    AttendanceReadModel,
    TeacherReadModel,
    TeacherAssignmentReadModel,

)

from app.contexts.school.factory import (
    ClassFactory,
    AttendanceFactory,
    GradeFactory,
    SubjectFactory,
)


def build_school_factories(db):
    class_read = ClassReadModel(db)
    subject_read_model = SubjectReadModel(db)
    attendance_read = AttendanceReadModel(db)
    teacher_read = TeacherReadModel(db)
    teacher_assignment_read = TeacherAssignmentReadModel(db)
    class_factory = ClassFactory(
        class_read_model=class_read,
        teacher_read_model=teacher_read,
    )
    attendance_factory = AttendanceFactory(
        class_read_model=class_read,
        attendance_read_model=attendance_read,
    )
    grade_factory = GradeFactory(
        class_read_model=class_read,
        subject_read_model=subject_read_model,
        teacher_assignment_read_model=teacher_assignment_read,
    )

    subject_factory = SubjectFactory(
        subject_read_model=subject_read_model,
    )

    return class_factory, attendance_factory, grade_factory, subject_factory