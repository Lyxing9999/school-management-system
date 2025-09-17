
# from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory



# class InvalidStaffRoleException(AppBaseException):
#     def __init__(self, role: str):
#         super().__init__(
#             message=f"Invalid role for Staff creation: {role} ", 
#             severity=ErrorSeverity.MEDIUM,
#             category=ErrorCategory.BUSINESS_LOGIC,
#             user_message="The role is invalid for staff.",
#             details={"field": "role", "value": role},
#             hint="Verify the role or create the role if missing",
#             recoverable=True
#         )
