from __future__ import annotations

import math
from flask import Blueprint, request, g

from app.contexts.core.security.auth_utils import get_current_employee_id, get_current_user
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import login_required

from app.contexts.hrms.mapper.payroll_mapper import PayrollMapper


payroll_query_bp = Blueprint("payroll_query_bp", __name__)
mapper = PayrollMapper()


@payroll_query_bp.route("/payroll/runs", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin"])
@wrap_response
def list_payroll_runs():
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)

    items, total = g.hrms.payroll.list_runs(page=page, page_size=page_size)
    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.payroll_run_to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_payroll_run_records(rows)

    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@payroll_query_bp.route("/payroll/runs/<payroll_run_id>", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin"])
@wrap_response
def get_payroll_run(payroll_run_id: str):
    run = g.hrms.payroll.get_run(payroll_run_id=payroll_run_id)
    row = mapper.payroll_run_to_dto(run).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="payroll_run")


@payroll_query_bp.route("/payroll/payslips", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin", "employee", "manager"])
@wrap_response
def list_payslips():
    payroll_run_id = request.args.get("payroll_run_id")
    month = (request.args.get("month") or "").strip() or None
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)

    current_user = get_current_user()
    role = current_user["role"]

    employee_id = request.args.get("employee_id")
    if role == "employee":
        employee_id = str(get_current_employee_id())

    items, total = g.hrms.payroll.list_payslips(
        payroll_run_id=payroll_run_id,
        employee_id=employee_id,
        month=month,
        page=page,
        page_size=page_size,
    )
    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.payslip_to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_payslip_records(rows)

    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@payroll_query_bp.route("/payroll/payslips/<payslip_id>", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin", "employee", "manager"])
@wrap_response
def get_payslip(payslip_id: str):
    payslip = g.hrms.payroll.get_payslip(payslip_id=payslip_id)

    current_user = get_current_user()
    if current_user["role"] == "employee":
        current_employee_id = get_current_employee_id()
        if str(payslip.employee_id) != str(current_employee_id):
            raise ValueError("You can only view your own payslip")

    row = mapper.payslip_to_dto(payslip).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="payslip")
