from __future__ import annotations

from typing import Any

from flask import Blueprint, request, g

from app.contexts.core.security.auth_utils import get_current_user_oid
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.iam.auth.jwt_utils import login_required

from app.contexts.hrms.data_transfer.request.payroll_request import GeneratePayrollSchema
from app.contexts.hrms.mapper.payroll_mapper import PayrollMapper


payroll_command_bp = Blueprint("payroll_command_bp", __name__)
mapper = PayrollMapper()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@payroll_command_bp.route("/payroll/runs/generate", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin"])
@wrap_response
def generate_monthly_payroll():
    actor_id = get_current_user_oid()
    payload = pydantic_converter.convert_to_model(request.json, GeneratePayrollSchema)

    result = g.hrms.payroll.generate_monthly(
        month=payload.month,
        generated_by=actor_id,
    )

    payroll_run = mapper.payroll_run_to_dto(result["payroll_run"]).model_dump(mode="json")
    g.hrms.response_enricher.enrich_single(payroll_run, kind="payroll_run")

    payslips = [mapper.payslip_to_dto(x).model_dump(mode="json") for x in result["payslips"]]
    g.hrms.response_enricher.enrich_payslip_records(payslips)

    meta = result.get("meta") if isinstance(result, dict) else {}
    meta = meta if isinstance(meta, dict) else {}
    skipped_employees = meta.get("skipped_employees")
    skipped_employees = skipped_employees if isinstance(skipped_employees, list) else []

    employee_count = _safe_int(meta.get("employee_count"))
    generated_count = _safe_int(meta.get("generated_count"), default=len(payslips))
    total_amount = round(sum(_safe_float(item.get("net_salary")) for item in payslips), 2)

    lifecycle = payroll_run.get("lifecycle")
    lifecycle = lifecycle if isinstance(lifecycle, dict) else {}

    # Keep a structured payload while preserving legacy flat fields
    # consumed by older frontend screens.
    return {
        "payroll_run": payroll_run,
        "payslips": payslips,
        "meta": {
            "employee_count": employee_count,
            "generated_count": generated_count,
            "skipped_employees": skipped_employees,
            "total_amount": total_amount,
        },
        "id": payroll_run.get("id"),
        "run_id": payroll_run.get("id"),
        "month": payroll_run.get("month"),
        "payroll_month": payroll_run.get("payroll_month"),
        "payroll_run_label": payroll_run.get("payroll_run_label"),
        "status": payroll_run.get("status"),
        "generated_by": payroll_run.get("generated_by"),
        "generated_by_name": payroll_run.get("generated_by_name"),
        "total_employees": employee_count,
        "generated_count": generated_count,
        "total_amount": total_amount,
        "generated_at": lifecycle.get("created_at"),
    }


@payroll_command_bp.route("/payroll/runs/<payroll_run_id>/finalize", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin"])
@wrap_response
def finalize_payroll_run(payroll_run_id: str):
    actor_id = get_current_user_oid()
    run = g.hrms.payroll.finalize(payroll_run_id=payroll_run_id, actor_id=actor_id)
    row = mapper.payroll_run_to_dto(run).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="payroll_run")


@payroll_command_bp.route("/payroll/runs/<payroll_run_id>/mark-paid", methods=["POST"], strict_slashes=False)
@login_required(allowed_roles=["payroll_manager", "hr_admin"])
@wrap_response
def mark_payroll_run_paid(payroll_run_id: str):
    actor_id = get_current_user_oid()
    run = g.hrms.payroll.mark_paid(payroll_run_id=payroll_run_id, actor_id=actor_id)
    row = mapper.payroll_run_to_dto(run).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="payroll_run")
