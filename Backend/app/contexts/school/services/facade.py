from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.contexts.school.services.use_cases.class_service import ClassService
    from app.contexts.school.services.use_cases.enrollment_service import EnrollmentService
    from app.contexts.school.services.use_cases.subject_service import SubjectService
    from app.contexts.school.services.use_cases.schedule_service import ScheduleService
    from app.contexts.school.services.use_cases.attendance_service import AttendanceService
    from app.contexts.school.services.use_cases.grade_service import GradeService
    from app.contexts.school.services.use_cases.teacher_assignment_service import TeacherAssignmentService

@dataclass(slots=True)
class SchoolFacade:
    class_service: ClassService
    enrollment_service: EnrollmentService
    subject_service: SubjectService
    schedule_service: ScheduleService
    attendance_service: AttendanceService
    grade_service: GradeService
    teacher_assignment_service: TeacherAssignmentService