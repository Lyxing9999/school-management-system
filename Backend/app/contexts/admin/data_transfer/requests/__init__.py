from .iam_schemas import (
    AdminCreateUserSchema,
    AdminSetUserStatusSchema,
    AdminUpdateUserSchema
)

from .staff_schemas import (
    AdminCreateStaffSchema,
    AdminUpdateStaffSchema,
)

from .student_schemas import (
    AdminCreateStudentSchema,
    AdminUpdateStudentSchema,
)

from .class_schemas import (
    AdminCreateClassSchema,
    AdminUpdateClassSchema,
    AdminAssignTeacherToClassSchema,
    AdminUnAssignTeacherToClassSchema,
    AdminEnrollStudentToClassSchema,
    AdminUpdateClassRelationsSchema,
    AdminSetClassStatusSchema
)

from .subject_schemas import (
    AdminCreateSubjectSchema,
    AdminUpdateSubjectSchema,
)

from .schedule_schemas import (
    AdminCreateScheduleSlotSchema,
    AdminUpdateScheduleSlotSchema,
    AdminAssignScheduleSlotSubjectSchema
)

from .assignment_requests import (
    AdminAssignSubjectTeacherRequest,
    AdminUnassignSubjectTeacherRequest,
)

__all__ = [
    # IAM
    "AdminCreateUserSchema",
    "AdminSetUserStatusSchema",
    "AdminUpdateUserSchema",

    # Staff
    "AdminCreateStaffSchema",
    "AdminUpdateStaffSchema",

    # Student
    "AdminCreateStudentSchema",
    "AdminUpdateStudentSchema",

    # Class
    "AdminCreateClassSchema",
    "AdminUpdateClassSchema",
    "AdminAssignTeacherToClassSchema",
    "AdminUnAssignTeacherToClassSchema",
    "AdminEnrollStudentToClassSchema",
    "AdminUpdateClassRelationsSchema",
    "AdminSetClassStatusSchema",

    # Subject
    "AdminCreateSubjectSchema",
    "AdminUpdateSubjectSchema",

    # Schedule
    "AdminCreateScheduleSlotSchema",
    "AdminUpdateScheduleSlotSchema",
    "AdminAssignScheduleSlotSubjectSchema",

    # teacher Assignment subject
    "AdminAssignSubjectTeacherRequest",
    "AdminUnassignSubjectTeacherRequest",
]