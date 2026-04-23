from __future__ import annotations

import math
from flask import Blueprint, request, g

from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import login_required

from app.contexts.hrms.mapper.employee_mapper import EmployeeMapper

employee_query_bp = Blueprint("employee_query_bp", __name__)
mapper = EmployeeMapper()


@employee_query_bp.route("/employees", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin"])
@wrap_response
def list_employees():
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)
    with_accounts = (request.args.get("with_accounts") or "false").lower() == "true"

    include_deleted = (request.args.get("include_deleted") or "false").lower() == "true"
    deleted_only = (request.args.get("deleted_only") or "false").lower() == "true"
    show_deleted = "all" if include_deleted else ("deleted" if deleted_only else "active")

    if with_accounts:
        items, total = g.hrms.employee.list_with_accounts(
            q=q,
            page=page,
            page_size=page_size,
            show_deleted=show_deleted,
        )

        total_pages = max(1, math.ceil(int(total) / page_size))
        mapped_items: list[dict] = []
        employee_rows: list[dict] = []
        account_rows: list[dict] = []

        for item in items:
            employee_row = mapper.to_dto(item["employee"]).model_dump(mode="json")
            account_row = dict(item.get("account") or {})

            mapped_items.append(
                {
                    "employee": employee_row,
                    "account": account_row or None,
                }
            )
            employee_rows.append(employee_row)
            if account_row:
                account_rows.append(account_row)

        g.hrms.response_enricher.enrich_employee_records(employee_rows)
        if account_rows:
            g.hrms.response_enricher.enrich_employee_account_records(account_rows)

        return {
            "items": mapped_items,
            "total": int(total),
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    items, total = g.hrms.employee.list(
        q=q,
        page=page,
        page_size=page_size,
        show_deleted=show_deleted,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(item).model_dump(mode="json") for item in items]
    g.hrms.response_enricher.enrich_employee_records(rows)

    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@employee_query_bp.route("/employees/<employee_id>", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin"])
@wrap_response
def get_employee(employee_id: str):
    employee = g.hrms.employee.get(employee_id=employee_id)
    row = mapper.to_dto(employee).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="employee")


@employee_query_bp.route("/employees/<employee_id>/account", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin"])
@wrap_response
def get_employee_account(employee_id: str):
    account = g.hrms.employee.get_account(employee_id=employee_id)
    if not account:
        return None
    row = dict(account)
    g.hrms.response_enricher.enrich_employee_account_records([row])
    return row


@employee_query_bp.route("/employees/me", methods=["GET"], strict_slashes=False)
@employee_query_bp.route("/employee/me", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["employee", "manager", "payroll_manager", "hr_admin"])
@wrap_response
def get_my_employee_profile():
    user_id = get_current_user_id()
    employee = g.hrms.employee.get_my_profile(user_id=user_id)
    row = mapper.to_dto(employee).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="employee")






@employee_query_bp.route("/employee-accounts", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin"])
@wrap_response
def list_employee_accounts():
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)

    include_deleted = (request.args.get("include_deleted") or "false").lower() == "true"
    deleted_only = (request.args.get("deleted_only") or "false").lower() == "true"
    show_deleted = "all" if include_deleted else ("deleted" if deleted_only else "active")
    status = (request.args.get("status") or "").strip() or None

    items, total = g.hrms.employee.list_accounts(
        page=page,
        page_size=page_size,
        search=q,
        show_deleted=show_deleted,
        status=status,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [dict(item or {}) for item in items]
    g.hrms.response_enricher.enrich_employee_account_records(rows)

    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
