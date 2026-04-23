from __future__ import annotations

import math
from flask import Blueprint, request, g

from app.contexts.core.security.auth_utils import get_current_employee_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import login_required

from app.contexts.hrms.data_transfer.response.leave_response import (
    LeaveBalanceDTO,
    LeaveSummaryDTO,
)
from app.contexts.hrms.mapper.leave_mapper import LeaveMapper


leave_query_bp = Blueprint("leave_query_bp", __name__)
mapper = LeaveMapper()


@leave_query_bp.route("/leave-requests", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "manager"])
@wrap_response
def list_leave_requests():
    employee_id = request.args.get("employee_id")
    status = (request.args.get("status") or "").strip() or None
    include_deleted = (request.args.get("include_deleted") or "false").lower() == "true"
    deleted_only = (request.args.get("deleted_only") or "false").lower() == "true"
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)

    items, total = g.hrms.leave.list(
        employee_id=employee_id,
        status=status,
        include_deleted=include_deleted,
        deleted_only=deleted_only,
        page=page,
        page_size=page_size,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_leave_records(rows)

    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@leave_query_bp.route("/leave-requests/my", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def list_my_leave_requests():
    employee_id = get_current_employee_id()
    status = (request.args.get("status") or "").strip() or None
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)

    items, total = g.hrms.leave.list_my(
        employee_id=employee_id,
        status=status,
        page=page,
        page_size=page_size,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_leave_records(rows)

    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@leave_query_bp.route("/leave-requests/<leave_id>", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "hr_admin", "payroll_manager"])
@wrap_response
def get_leave_request(leave_id: str):
    leave = g.hrms.leave.get(leave_id=leave_id)
    row = mapper.to_dto(leave).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="leave")


@leave_query_bp.route("/leave-requests/pending-reviews", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["manager", "hr_admin"])
@wrap_response
def list_pending_leave_requests():
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)

    items, total = g.hrms.leave.list_pending(
        page=page,
        page_size=page_size,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_leave_records(rows)

    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@leave_query_bp.route("/leave-requests/my-summary", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def get_my_leave_summary():
    employee_id = get_current_employee_id()
    result = g.hrms.leave.get_my_summary(employee_id=employee_id)
    return LeaveSummaryDTO(**result)


@leave_query_bp.route("/leave-requests/my-balance", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def get_my_leave_balance():
    employee_id = get_current_employee_id()
    result = g.hrms.leave.get_my_balance(employee_id=employee_id)
    return LeaveBalanceDTO(**result)
