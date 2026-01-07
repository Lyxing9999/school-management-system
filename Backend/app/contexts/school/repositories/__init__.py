from app.contexts.school.repositories.attendance_repository import (
    IAttendanceRepository,
    MongoAttendanceRepository,
)
from app.contexts.school.repositories.class_repository import (
    IClassSectionRepository,
    MongoClassSectionRepository,
)

from app.contexts.school.repositories.grade_repository import (
    IGradeRepository,
    MongoGradeRepository,
)
from app.contexts.school.repositories.schedule_repository import (
    IScheduleRepository,
    MongoScheduleRepository,
)
from app.contexts.school.repositories.subject_repository import (
    ISubjectRepository,
    MongoSubjectRepository,
)
from app.contexts.school.repositories.teacher_assignment_repository import (
    TeacherAssignmentRepository,
)

__all__ = [
    "IAttendanceRepository",
    "MongoAttendanceRepository",
    "IClassSectionRepository",
    "MongoClassSectionRepository",
    "IGradeRepository",
    "MongoGradeRepository",
    "IScheduleRepository",
    "MongoScheduleRepository",
    "ISubjectRepository",
    "MongoSubjectRepository",
    "TeacherAssignmentRepository",
]