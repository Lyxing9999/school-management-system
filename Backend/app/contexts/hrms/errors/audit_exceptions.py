from app.contexts.core.errors import AppBaseException


class AuditEntityTypeRequiredException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="entity_type is required",
            error_code="AUDIT_ENTITY_TYPE_REQUIRED",
            status_code=400,
            user_message="Entity type is required.",
        )
