# app/contexts/admin/routes/dashboard_route.py
from __future__ import annotations

from datetime import datetime
from flask import request, g

from app.contexts.admin.routes import admin_bp
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.admin.data_transfer.response import AdminDashboardDTO


def _parse_date_arg(value: str | None) -> datetime | None:
    """
    Small helper to parse date query params.

    Accepts:
      - "YYYY-MM-DD"
      - full ISO "2025-11-25T00:00:00"
    Returns datetime or None.
    """
    if not value:
        return None
    try:
        # If only date, treat as midnight
        if len(value) == 10:
            return datetime.fromisoformat(value + "T00:00:00")
        return datetime.fromisoformat(value)
    except ValueError:
        # For MVP: ignore invalid and just return None
        return None


@admin_bp.route("/dashboard", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_dashboard():
    """
    GET /admin/dashboard

    Optional query params:
      - date_from=YYYY-MM-DD
      - date_to=YYYY-MM-DD
      - term=S1 / S2 / SUMMER / etc. (must match what you store in GradeRecord.term)

    Response is shaped by AdminDashboardDTO:
    {
      "overview": { ... },
      "attendance": { ... },
      "grades": { ... },
      "schedule": { ... }
    }
    """

    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")
    term = request.args.get("term")  # can be None

    date_from = _parse_date_arg(date_from_str)
    date_to = _parse_date_arg(date_to_str)

    raw = g.admin.dashboard_read_model.get_admin_dashboard(date_from=date_from, date_to=date_to, term=term)

    dto = AdminDashboardDTO(**raw)
    return dto