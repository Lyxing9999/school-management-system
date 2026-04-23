from __future__ import annotations

from flask import Blueprint, request, g

from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import login_required
from app.contexts.hrms.mapper.work_location_mapper import WorkLocationMapper


work_location_query_bp = Blueprint("work_location_query_bp", __name__)
mapper = WorkLocationMapper()


def _parse_bool_arg(name: str) -> bool | None:
    raw = request.args.get(name)
    if raw is None:
        return None

    normalized = str(raw).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return None


@work_location_query_bp.route("/work-locations", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "employee", "manager", "payroll_manager"])
@wrap_response
def list_work_locations():
    q = request.args.get("q", "")
    status = request.args.get("status", "all")

    include_deleted = _parse_bool_arg("include_deleted")
    deleted_only = _parse_bool_arg("deleted_only")
    is_active = _parse_bool_arg("is_active")

    items = g.hrms.work_location.list(
        q=q,
        status=status,
        include_deleted=include_deleted,
        deleted_only=deleted_only,
        is_active=is_active,
    )
    rows = [mapper.to_dto(item).model_dump(mode="json") for item in items]
    g.hrms.response_enricher.enrich_work_location_records(rows)
    return rows


@work_location_query_bp.route("/work-locations/<location_id>", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "employee", "manager", "payroll_manager"])
@wrap_response
def get_work_location(location_id: str):
    item = g.hrms.work_location.get(location_id=location_id)
    row = mapper.to_dto(item).model_dump(mode="json")
    return g.hrms.response_enricher.enrich_single(row, kind="work_location")


@work_location_query_bp.route("/work-locations/active", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "employee", "manager", "payroll_manager"])
@wrap_response
def get_active_work_location():
    item = g.hrms.work_location.get_active()
    row = mapper.to_dto(item).model_dump(mode="json") if item else None
    return g.hrms.response_enricher.enrich_single(row, kind="work_location")




@work_location_query_bp.route("/work-locations/select-options", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "employee", "manager", "payroll_manager"])
@wrap_response
def list_work_location_select_options():
    items = g.hrms.work_location.list(q="", status="active")
    return [
        {
            "value": str(item.id),
            "label": item.name,
        }
        for item in items
        if not item.lifecycle.deleted_at
    ]
