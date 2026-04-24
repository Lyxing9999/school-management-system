from __future__ import annotations

import math

from flask import Blueprint, request, g

from app.contexts.iam.auth.jwt_utils import login_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.time_utils import ensure_utc
from app.contexts.hrms.mapper.audit_log_mapper import AuditLogMapper


audit_query_bp = Blueprint("audit_query_bp", __name__)
mapper = AuditLogMapper()


@audit_query_bp.route("/audit-logs", methods=["GET"], strict_slashes=False)
@login_required(allowed_roles=["hr_admin", "manager", "payroll_manager"])
@wrap_response
def list_audit_logs():
    entity_type = (request.args.get("entity_type") or "").strip() or None
    action = (request.args.get("action") or "").strip().lower() or None

    actor_id_raw = (request.args.get("actor_id") or "").strip() or None
    entity_id_raw = (request.args.get("entity_id") or "").strip() or None

    actor_id = mongo_converter.convert_to_object_id(actor_id_raw) if actor_id_raw else None
    entity_id = mongo_converter.convert_to_object_id(entity_id_raw) if entity_id_raw else None

    start_at_raw = (request.args.get("start_at") or "").strip() or None
    end_at_raw = (request.args.get("end_at") or "").strip() or None
    start_at = ensure_utc(start_at_raw) if start_at_raw else None
    end_at = ensure_utc(end_at_raw) if end_at_raw else None

    include_deleted = (request.args.get("include_deleted") or "false").lower() == "true"
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 20), 1), 200)

    items, total = g.hrms.audit.list(
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        action=action,
        start_at=start_at,
        end_at=end_at,
        include_deleted=include_deleted,
        page=page,
        page_size=page_size,
    )

    rows = [mapper.to_dto(item).model_dump(mode="json") for item in items]
    g.hrms.response_enricher.enrich_audit_records(rows)

    total_pages = max(1, math.ceil(int(total) / page_size))
    return {
        "items": rows,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
