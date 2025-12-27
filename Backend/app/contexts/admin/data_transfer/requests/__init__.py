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
    AdminUpdateClassRelationsSchema
)

from .subject_schemas import (
    AdminCreateSubjectSchema,
    AdminUpdateSubjectSchema,
)

from .schedule_schemas import (
    AdminCreateScheduleSlotSchema,
    AdminUpdateScheduleSlotSchema,
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

    # Subject
    "AdminCreateSubjectSchema",
    "AdminUpdateSubjectSchema",

    # Schedule
    "AdminCreateScheduleSlotSchema",
    "AdminUpdateScheduleSlotSchema",
]