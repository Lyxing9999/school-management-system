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

from app.contexts.hrms.data_transfer.request.overtime_request import (
    OvertimeCreateSchema,
    OvertimeApproveSchema,
    OvertimeRejectSchema,
)
from app.contexts.hrms.mapper.overtime_mapper import OvertimeMapper


overtime_command_bp = Blueprint("overtime_command_bp", __name__)
mapper = OvertimeMapper()


def _maybe_current_employee_id():
    try:
        return get_current_employee_id()
    except Exception:
        return None


@overtime_command_bp.route("/overtime-requests", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def create_overtime_request():
    employee_id = get_current_employee_id()
    payload = pydantic_converter.convert_to_model(request.json, OvertimeCreateSchema)

    overtime = g.hrms.overtime.create(
        employee_id=employee_id,
        payload=payload,
    )
    return mapper.to_dto(overtime).model_dump(mode="json")


@overtime_command_bp.route("/overtime-requests/<overtime_id>/approve", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["manager", "hr_admin"])
@wrap_response
def approve_overtime_request(overtime_id: str):
    current_user = get_current_user()
    actor_user_id = get_current_user_oid()
    actor_role = str(current_user.get("role") or "").strip().lower()
    actor_employee_id = _maybe_current_employee_id()
    reviewer_id = actor_employee_id or actor_user_id

    payload = pydantic_converter.convert_to_model(request.json, OvertimeApproveSchema)

    overtime = g.hrms.overtime.approve(
        overtime_id=overtime_id,
        manager_id=reviewer_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        approved_hours=payload.approved_hours,
        comment=payload.comment,
    )
    return mapper.to_dto(overtime).model_dump(mode="json")


@overtime_command_bp.route("/overtime-requests/<overtime_id>/reject", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["manager", "hr_admin"])
@wrap_response
def reject_overtime_request(overtime_id: str):
    current_user = get_current_user()
    actor_user_id = get_current_user_oid()
    actor_role = str(current_user.get("role") or "").strip().lower()
    actor_employee_id = _maybe_current_employee_id()
    reviewer_id = actor_employee_id or actor_user_id

    payload = pydantic_converter.convert_to_model(request.json, OvertimeRejectSchema)

    overtime = g.hrms.overtime.reject(
        overtime_id=overtime_id,
        manager_id=reviewer_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        comment=payload.comment,
    )
    return mapper.to_dto(overtime).model_dump(mode="json")


@overtime_command_bp.route("/overtime-requests/<overtime_id>/cancel", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def cancel_overtime_request(overtime_id: str):
    current_user = get_current_user()
    actor_user_id = get_current_user_oid()
    actor_role = str(current_user.get("role") or "").strip().lower()

    actor_employee_id = None
    if actor_role == "employee":
        actor_employee_id = get_current_employee_id()
    elif actor_role in {"manager", "payroll_manager"}:
        actor_employee_id = _maybe_current_employee_id()

    overtime = g.hrms.overtime.cancel(
        overtime_id=overtime_id,
        actor_employee_id=actor_employee_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
    )
    return mapper.to_dto(overtime).model_dump(mode="json")
