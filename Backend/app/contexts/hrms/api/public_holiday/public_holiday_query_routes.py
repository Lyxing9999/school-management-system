from __future__ import annotations

from flask import Blueprint, request, g

from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import login_required
from app.contexts.hrms.mapper.public_holiday_mapper import PublicHolidayMapper
from datetime import date

public_holiday_query_bp = Blueprint("public_holiday_query_bp", __name__)
mapper = PublicHolidayMapper()


@public_holiday_query_bp.route("/public-holidays", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "employee", "manager", "payroll_manager"])
@wrap_response
def list_public_holidays():
    year = request.args.get("year", type=int)
    include_deleted = request.args.get("include_deleted", "false").lower() == "true"
    deleted_only = request.args.get("deleted_only", "false").lower() == "true"

    items = g.hrms.public_holiday.list(
        year=year,
        include_deleted=include_deleted,
        deleted_only=deleted_only,
    )
    rows = [mapper.to_dto(item).model_dump(mode="json") for item in items]
    g.hrms.response_enricher.enrich_public_holiday_records(rows)
    return rows


@public_holiday_query_bp.route("/public-holidays/<holiday_id>", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "employee", "manager", "payroll_manager"])
@wrap_response
def get_public_holiday(holiday_id: str):
    holiday = g.hrms.public_holiday.get(holiday_id=holiday_id)
    row = mapper.to_dto(holiday).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="public_holiday")


@public_holiday_query_bp.route("/public-holidays/by-date", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "employee", "manager", "payroll_manager"])
@wrap_response
def check_public_holiday_by_date():
    holiday_date_str = request.args.get("date")
    holiday_date = date.fromisoformat(holiday_date_str)
    holiday = g.hrms.public_holiday.check_by_date(date=holiday_date)
    row = mapper.to_dto(holiday).model_dump(mode="json") if holiday else None
    return g.hrms.response_enricher.enrich_single(row, kind="public_holiday")
