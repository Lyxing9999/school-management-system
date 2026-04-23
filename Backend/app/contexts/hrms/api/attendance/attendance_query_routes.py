from __future__ import annotations

import math
from flask import Blueprint, request, g

from app.contexts.core.security.auth_utils import (
    get_current_employee_id,
    get_current_user_id,
)
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import login_required

from app.contexts.hrms.mapper.attendance_mapper import AttendanceMapper
attendance_query_bp = Blueprint("attendance_query_bp", __name__)
mapper = AttendanceMapper()


@attendance_query_bp.route("/attendance/me", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "hr_admin", "manager", "payroll_manager"])
@wrap_response
def get_my_attendance():
    employee_id = get_current_employee_id()

    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)
    status = (request.args.get("status") or "").strip() or None
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    items, total = g.hrms.attendance.get_my_attendance(
        employee_id=employee_id,
        page=page,
        page_size=page_size,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_attendance_records(rows)

    return {
        "items": rows,
        "pagination": {
            "total": int(total),
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }


@attendance_query_bp.route("/attendance", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "payroll_manager"])
@wrap_response
def list_attendance():
    employee_id = request.args.get("employee_id")
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)
    status = (request.args.get("status") or "").strip() or None
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    include_deleted = (request.args.get("include_deleted") or "false").lower() == "true"
    deleted_only = (request.args.get("deleted_only") or "false").lower() == "true"

    items, total = g.hrms.attendance.list_attendance(
        employee_id=employee_id,
        page=page,
        page_size=page_size,
        status=status,
        start_date=start_date,
        end_date=end_date,
        include_deleted=include_deleted,
        deleted_only=deleted_only,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_attendance_records(rows)

    return {
        "items": rows,
        "pagination": {
            "total": int(total),
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }


@attendance_query_bp.route("/attendance/team", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["manager", "hr_admin"])
@wrap_response
def get_team_attendance():
    manager_user_id = get_current_user_id()

    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)
    status = (request.args.get("status") or "").strip() or None
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    items, total = g.hrms.attendance.get_team_attendance(
        manager_user_id=manager_user_id,
        page=page,
        page_size=page_size,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_attendance_records(rows)

    return {
        "items": rows,
        "pagination": {
            "total": int(total),
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }
@attendance_query_bp.route("/attendance/reports/wrong-location", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "manager"])
@wrap_response
def get_wrong_location_report():
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)
    review_status = (
        (request.args.get("review_status") or "").strip()
        or (request.args.get("status") or "").strip()
        or None
    )
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    items, total = g.hrms.attendance.get_wrong_location_report(
        page=page,
        page_size=page_size,
        review_status=review_status,
        start_date=start_date,
        end_date=end_date,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_attendance_records(rows)

    return {
        "items": rows,
        "pagination": {
            "total": int(total),
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }



@attendance_query_bp.route("/attendance/me/today", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "hr_admin", "manager", "payroll_manager"])
@wrap_response
def get_my_attendance_today():
    employee_id = get_current_employee_id()

    item = g.hrms.attendance.get_my_attendance_today(
        employee_id=employee_id,
    )

    row = mapper.to_dto(item).model_dump(mode="json") if item else None
    row = g.hrms.response_enricher.enrich_single(row, kind="attendance")
    return {"item": row}
