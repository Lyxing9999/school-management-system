from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.contexts.school.services.use_cases import (
    ClassService,
    EnrollmentService,
    SubjectService,
    ScheduleService,
    AttendanceService,
    GradeService,
    ClassRelationsService
    )

@dataclass(slots=True)
class SchoolFacade:
    class_service: ClassService
    enrollment_service: EnrollmentService
    subject_service: SubjectService
    schedule_service: ScheduleService
    attendance_service: AttendanceService
    grade_service: GradeService
    class_relations_service: ClassRelationsService