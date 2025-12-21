from typing import Any, Dict, Optional, Literal

from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory

DeleteMode = Literal["soft", "hard", "restore", "status_change"]

class LifecyclePolicyDeniedException(AppBaseException):
    """
    Raised when a lifecycle policy blocks an operation (soft/hard delete, restore, etc.).
    Use this for ALL "cannot delete because relationships exist" cases.
    """

    def __init__(
        self,
        entity: str,                 
        entity_id: str,
        mode: DeleteMode,          
        reasons: Dict[str, Any], 
        recommended: Optional[DeleteMode] = None,
        hint: str | None = None,
    ):
        reason_text = ", ".join([f"{k}={v}" for k, v in reasons.items()]) if reasons else "policy denied"

        user_message = f"Cannot {mode} {entity} because: {reason_text}."
        if recommended:
            user_message += f" Recommended: {recommended}."

        super().__init__(
            message=f"Lifecycle policy denied: {entity} {entity_id} mode={mode} reasons={reasons} recommended={recommended}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=user_message,
            details={
                "entity": entity,
                "entity_id": entity_id,
                "mode": mode,
                "reasons": reasons,
                "recommended": recommended,
            },
            hint=hint or "Resolve blockers (unassign/remove relationships) and try again.",
            recoverable=True,
        )