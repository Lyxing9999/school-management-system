from __future__ import annotations

import math
from flask import Blueprint, request, g

from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import login_required

from app.contexts.hrms.mapper.deduction_rule_mapper import DeductionRuleMapper


deduction_rule_query_bp = Blueprint("deduction_rule_query_bp", __name__)
mapper = DeductionRuleMapper()


@deduction_rule_query_bp.route("/deduction-rules", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "payroll_manager"])
@wrap_response
def list_deduction_rules():
    type = (request.args.get("type") or "").strip() or None
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"

    include_deleted = (request.args.get("include_deleted") or "false").lower() == "true"
    deleted_only = (request.args.get("deleted_only") or "false").lower() == "true"

    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)

    items, total = g.hrms.deduction_rule.list(
        type=type,
        is_active=is_active,
        include_deleted=include_deleted,
        deleted_only=deleted_only,
        page=page,
        page_size=page_size,
    )

    total_pages = max(1, math.ceil(int(total) / page_size))
    rows = [mapper.to_dto(x).model_dump(mode="json") for x in items]
    g.hrms.response_enricher.enrich_deduction_rule_records(rows)

    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@deduction_rule_query_bp.route("/deduction-rules/<rule_id>", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "payroll_manager"])
@wrap_response
def get_deduction_rule(rule_id: str):
    rule = g.hrms.deduction_rule.get(rule_id=rule_id)
    row = mapper.to_dto(rule).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="deduction_rule")


@deduction_rule_query_bp.route("/deduction-rules/applicable", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "payroll_manager"])
@wrap_response
def find_applicable_rule():
    type = (request.args.get("type") or "").strip()
    minutes = int(request.args.get("minutes") or 0)

    rule = g.hrms.deduction_rule.find_applicable(
        type=type,
        minutes=minutes,
    )
    row = mapper.to_dto(rule).model_dump(mode="json") if rule else None
    return g.hrms.response_enricher.enrich_single(row, kind="deduction_rule")
