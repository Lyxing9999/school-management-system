from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory



class InvalidRoleToFindException(AppBaseException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Invalid role to find: {role}",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.INFO,
            error_code="INVALID_ROLE_TO_FIND_ERROR",
            user_message=f"The provided role '{role}' is invalid.",
            details={"field": "role", "value": role},
            recoverable=True
        )

class StaffRoleException(AppBaseException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Invalid role for Staff creation: {role} ", 
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The role is invalid for staff.",
            details={"field": "role", "value": role},
            hint="Verify the role or create the role if missing",
            recoverable=True
        )


# class ClassTimeException(AppBaseException):
#     def __init__(self, start_time: str, end_time: str, message: str = "Class time is invalid"):
#         self.start_time = start_time
#         self.end_time = end_time
#         super().__init__(
#             message=message,
#             severity=ErrorSeverity.ERROR,
#             category=ErrorCategory.BUSINESS,
#             error_code="CLASS_TIME_ERROR",
#             user_message=f"The provided class time '{start_time}' to '{end_time}' is invalid.",
#             details={"field": "class_time", "value": start_time} | {"field": "class_time", "value": end_time},
#             recoverable=True
#         )



# class ClassDayException(AppBaseException):
#     def __init__(self, day: str, message: str = "Class day is invalid"):
#         self.day = day
#         super().__init__(
#             message=message,
#             severity=ErrorSeverity.ERROR,
#             category=ErrorCategory.BUSINESS,
#             error_code="CLASS_DAY_ERROR",
#             user_message=f"The provided class day '{day}' is invalid.",
#             details={"field": "class_day", "value": day},
#             recoverable=True
#         )


# class ClassCreateRequiredException(AppBaseException):
#     def __init__(self, field: str, message: str = "Class create is invalid"):
#         super().__init__(
#             message=message,
#             severity=ErrorSeverity.ERROR,
#             category=ErrorCategory.BUSINESS,
#             error_code="CLASS_CREATE_REQUIRED_ERROR",
#             user_message=f"The provided class create is invalid.",
#             details={"field": field, "value": ""},
#             recoverable=True
#         )