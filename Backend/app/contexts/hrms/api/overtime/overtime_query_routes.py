from __future__ import annotations

from flask import Blueprint, request, g

from app.contexts.core.security.auth_utils import get_current_employee_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import login_required
from app.contexts.hrms.mapper.overtime_mapper import OvertimeMapper


overtime_query_bp = Blueprint("overtime_query_bp", __name__)
mapper = OvertimeMapper()


@overtime_query_bp.route("/overtime-requests", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "manager"])
@wrap_response
def list_overtime_requests():
    employee_id = request.args.get("employee_id")
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    items, total = g.hrms.overtime.list(
        employee_id=employee_id,
        status=status,
        page=page,
        limit=limit,
    )
    rows = [mapper.to_dto(item).model_dump(mode="json") for item in items]
    g.hrms.response_enricher.enrich_overtime_records(rows)

    return {
        "items": rows,
        "total": total,
        "page": page,
        "limit": limit,
    }


@overtime_query_bp.route("/overtime-requests/my", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def list_my_overtime_requests():
    employee_id = get_current_employee_id()
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    items, total = g.hrms.overtime.list_my(
        employee_id=employee_id,
        status=status,
        page=page,
        limit=limit,
    )
    rows = [mapper.to_dto(item).model_dump(mode="json") for item in items]
    g.hrms.response_enricher.enrich_overtime_records(rows)

    return {
        "items": rows,
        "total": total,
        "page": page,
        "limit": limit,
    }


@overtime_query_bp.route("/overtime-requests/<overtime_id>", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "hr_admin", "payroll_manager"])
@wrap_response
def get_overtime_request(overtime_id: str):
    overtime = g.hrms.overtime.get(overtime_id=overtime_id)
    row = mapper.to_dto(overtime).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="overtime")


@overtime_query_bp.route("/overtime-requests/pending-approval", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["manager", "hr_admin"])
@wrap_response
def list_pending_approval_overtime_requests():
    employee_id = request.args.get("employee_id")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    items, total = g.hrms.overtime.list_pending_approval(
        employee_id=employee_id,
        page=page,
        limit=limit,
    )
    rows = [mapper.to_dto(item).model_dump(mode="json") for item in items]
    g.hrms.response_enricher.enrich_overtime_records(rows)

    return {
        "items": rows,
        "total": total,
        "page": page,
        "limit": limit,
    }


@overtime_query_bp.route("/overtime-requests/my-summary", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def get_my_overtime_summary():
    employee_id = get_current_employee_id()
    return g.hrms.overtime.get_my_summary(employee_id=employee_id)


@overtime_query_bp.route("/overtime-requests/payroll-approved", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin"])
@wrap_response
def list_approved_overtime_for_payroll():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    employee_id = request.args.get("employee_id")

    items = g.hrms.overtime.list_approved_for_payroll(
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id,
    )

    rows = [mapper.to_dto(item).model_dump(mode="json") for item in items]
    g.hrms.response_enricher.enrich_overtime_records(rows)
    return rows


@overtime_query_bp.route("/overtime-requests/payroll-summary", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin"])
@wrap_response
def get_overtime_payroll_summary():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    return g.hrms.overtime.get_payroll_summary(
        start_date=start_date,
        end_date=end_date,
    )
