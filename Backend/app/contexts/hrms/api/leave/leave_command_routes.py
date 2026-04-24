from __future__ import annotations

from flask import Blueprint, request, g

from app.contexts.core.security.auth_utils import (
    get_current_employee_id,
    get_current_user,
    get_current_user_oid,
)
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.iam.auth.jwt_utils import login_required

from app.contexts.hrms.data_transfer.request.leave_request import (
    LeaveSubmitSchema,
    LeaveApproveSchema,
    LeaveRejectSchema,
)
from app.contexts.hrms.mapper.leave_mapper import LeaveMapper


leave_command_bp = Blueprint("leave_command_bp", __name__)
mapper = LeaveMapper()


def _maybe_current_employee_id():
    try:
        return get_current_employee_id()
    except Exception:
        return None


@leave_command_bp.route("/leave-requests", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def submit_leave_request():
    employee_id = get_current_employee_id()
    payload = pydantic_converter.convert_to_model(request.json, LeaveSubmitSchema)

    leave = g.hrms.leave.submit(
        employee_id=employee_id,
        payload=payload,
    )
    return mapper.to_dto(leave)


@leave_command_bp.route("/leave-requests/<leave_id>/approve", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["manager", "hr_admin"])
@wrap_response
def approve_leave_request(leave_id: str):
    current_user = get_current_user()
    actor_role = str(current_user.get("role") or "").strip().lower()
    manager_user_id = get_current_user_oid()
    payload = pydantic_converter.convert_to_model(request.json, LeaveApproveSchema)

    leave = g.hrms.leave.approve(
        leave_id=leave_id,
        manager_user_id=manager_user_id,
        actor_role=actor_role,
        comment=payload.comment,
    )
    return mapper.to_dto(leave)


@leave_command_bp.route("/leave-requests/<leave_id>/reject", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["manager", "hr_admin"])
@wrap_response
def reject_leave_request(leave_id: str):
    manager_user_id = get_current_user_oid()
    payload = pydantic_converter.convert_to_model(request.json, LeaveRejectSchema)

    leave = g.hrms.leave.reject(
        leave_id=leave_id,
        manager_user_id=manager_user_id,
        comment=payload.comment,
    )
    return mapper.to_dto(leave)


@leave_command_bp.route("/leave-requests/<leave_id>/cancel", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def cancel_leave_request(leave_id: str):
    current_user = get_current_user()
    actor_role = str(current_user.get("role") or "").strip().lower()
    actor_user_id = get_current_user_oid()

    actor_employee_id = None
    if actor_role == "employee":
        actor_employee_id = get_current_employee_id()
    elif actor_role in {"manager", "payroll_manager"}:
        actor_employee_id = _maybe_current_employee_id()

    leave = g.hrms.leave.cancel(
        leave_id=leave_id,
        actor_employee_id=actor_employee_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
    )
    return mapper.to_dto(leave)
