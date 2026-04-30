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

from app.contexts.hrms.data_transfer.request.attendance_request import (
    AttendanceCheckInSchema,
    AttendanceCheckOutSchema,
    AttendanceApproveWrongLocationSchema,
    AttendanceApproveEarlyLeaveSchema,
)
from app.contexts.hrms.mapper.attendance_mapper import AttendanceMapper


attendance_command_bp = Blueprint("attendance_command_bp", __name__)
mapper = AttendanceMapper()


@attendance_command_bp.route("/attendance/check-in", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["employee", "hr_admin", "manager", "payroll_manager"])
@wrap_response
def check_in():
    employee_id = get_current_employee_id()
    actor_user_id = get_current_user_oid()
    payload = pydantic_converter.convert_to_model(request.json, AttendanceCheckInSchema)

    attendance = g.hrms.attendance.check_in(
        employee_id=employee_id,
        check_in_time=payload.check_in_time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        wrong_location_reason=payload.wrong_location_reason,
        late_reason=payload.late_reason,
        actor_user_id=actor_user_id,
    )

    return mapper.to_dto(attendance)


@attendance_command_bp.route("/attendance/check-out", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["employee", "hr_admin", "manager", "payroll_manager"])
@wrap_response
def check_out():
    employee_id = get_current_employee_id()
    actor_user_id = get_current_user_oid()
    payload = pydantic_converter.convert_to_model(request.json, AttendanceCheckOutSchema)

    attendance = g.hrms.attendance.check_out(
        employee_id=employee_id,
        check_out_time=payload.check_out_time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        early_leave_reason=payload.early_leave_reason,
        actor_user_id=actor_user_id,
    )

    return mapper.to_dto(attendance)


@attendance_command_bp.route("/attendance/<attendance_id>/wrong-location/review", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "manager"])
@wrap_response
def review_wrong_location(attendance_id: str):
    admin_id = get_current_user_oid()
    current_user = get_current_user()
    actor_role = str(current_user.get("role") or "").strip().lower()
    payload = pydantic_converter.convert_to_model(
        request.json,
        AttendanceApproveWrongLocationSchema,
    )

    attendance = g.hrms.attendance.approve_wrong_location(
        attendance_id=attendance_id,
        admin_id=admin_id,
        actor_role=actor_role,
        approved=payload.approved,
        comment=payload.comment,
        location_id=payload.location_id,
    )

    return mapper.to_dto(attendance)

@attendance_command_bp.route(
    "/attendance/<attendance_id>/early-leave/review",
    methods=["POST"],
    strict_slashes=False,
)
@login_required(allowed_roles=["hr_admin", "manager"])
@wrap_response
def review_early_leave(attendance_id: str):
    admin_id = get_current_user_oid()
    current_user = get_current_user()
    actor_role = str(current_user.get("role") or "").strip().lower()
    payload = pydantic_converter.convert_to_model(
        request.json,
        AttendanceApproveEarlyLeaveSchema,
    )
    attendance = g.hrms.attendance.review_early_leave(
        attendance_id=attendance_id,
        admin_id=admin_id,
        actor_role=actor_role,
        approved=payload.approved,
        comment=payload.comment,
    )
    return mapper.to_dto(attendance)
