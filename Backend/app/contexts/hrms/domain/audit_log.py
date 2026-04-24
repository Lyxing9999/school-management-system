from __future__ import annotations

from enum import Enum
from datetime import datetime
from bson import ObjectId

from app.contexts.shared.lifecycle.domain import Lifecycle


class AuditAction(str, Enum):
    ATTENDANCE_CHECK_IN = "attendance_check_in"
    ATTENDANCE_CHECK_OUT = "attendance_check_out"
    ATTENDANCE_WRONG_LOCATION_APPROVED = "attendance_wrong_location_approved"
    ATTENDANCE_WRONG_LOCATION_REJECTED = "attendance_wrong_location_rejected"
    ATTENDANCE_EARLY_LEAVE_APPROVED = "attendance_early_leave_approved"
    ATTENDANCE_EARLY_LEAVE_REJECTED = "attendance_early_leave_rejected"
    ATTENDANCE_MARKED_MISSING_CHECK_OUT = "attendance_marked_missing_check_out"
    OT_SUBMITTED = "ot_submitted"
    OT_APPROVED = "ot_approved"
    OT_REJECTED = "ot_rejected"
    OT_CANCELLED = "ot_cancelled"
    LEAVE_SUBMITTED = "leave_submitted"
    LEAVE_APPROVED = "leave_approved"
    LEAVE_REJECTED = "leave_rejected"
    LEAVE_CANCELLED = "leave_cancelled"
    PAYROLL_GENERATED = "payroll_generated"
    PAYROLL_FINALIZED = "payroll_finalized"
    PAYROLL_MARKED_PAID = "payroll_marked_paid"


class AuditLog:
    def __init__(
        self,
        *,
        entity_type: str,
        entity_id: ObjectId,
        action: AuditAction | str,
        actor_id: ObjectId | None,
        action_at: datetime,
        details: dict | None = None,
        id: ObjectId | None = None,
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self.id = id or ObjectId()
        self.entity_type = (entity_type or "").strip()
        self.entity_id = entity_id
        self.action = AuditAction(str(action).strip().lower())
        self.actor_id = actor_id
        self.action_at = action_at
        self.details = details or {}
        self.lifecycle = lifecycle or Lifecycle()

        if not self.entity_type:
            raise ValueError("entity_type is required")
