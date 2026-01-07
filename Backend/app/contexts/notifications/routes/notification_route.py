from flask import Blueprint, request
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.infra.database.db import get_db
from app.contexts.iam.auth.jwt_utils import login_required
from flask import g

from app.contexts.notifications.services.notification_service import NotificationService
from app.contexts.notifications.read_models.notification_read_model import NotificationReadModel
from app.contexts.notifications.utils.type_filter import parse_type_filter, parse_unread_only
notification_bp = Blueprint("notification_bp", __name__)


@notification_bp.route("", methods=["GET"])
@wrap_response
@login_required()
def list_notifications():
    user_id = str(g.user["id"])

    limit = int(request.args.get("limit") or 30)
    limit = max(1, min(limit, 100))

    notif_type = parse_type_filter()         
    unread_only = parse_unread_only()      

    rm = NotificationReadModel(get_db())
    items = rm.list_latest(
        user_id=user_id,
        limit=limit,
        type=notif_type,
        unread_only=unread_only,
    )
    return {"items": items}


@notification_bp.route("/unread-count", methods=["GET"])
@wrap_response
@login_required()
def unread_count():
    user_id = str(g.user["id"])
    notif_type = parse_type_filter()

    rm = NotificationReadModel(get_db())
    unread = rm.count_unread(user_id=user_id, type=notif_type)
    return {"unread": unread}

@notification_bp.route("/<id>/read", methods=["POST"])
@wrap_response
@login_required()
def mark_read(id: str):
    user_id = str(g.user["id"])
    rm = NotificationReadModel(get_db())
    rm.mark_read(user_id=user_id, notification_id=id)
    return {"ok": True}

@notification_bp.route("/read-all", methods=["POST"])
@wrap_response
@login_required()
def mark_all_read():
    user_id = str(g.user["id"])
    notif_type = parse_type_filter()

    rm = NotificationReadModel(get_db())
    count = rm.mark_all_read(user_id=user_id, type=notif_type)
    return {"ok": True, "updated": count}
    
# Optional: easy testing endpoint
@notification_bp.route("/test", methods=["POST"])
@wrap_response
@login_required()
def test_notification():
    db = get_db()
    svc = NotificationService(db)

    svc.create_for_user(
        user_id=str(g.user["id"]),
        role=str(g.user["role"]),
        type="test",
        title="Test notification",
        message="This is a realtime test from /api/notifications/test",
        entity_type="system",
        entity_id=None,
        data={"hello": "world"},
    )
    return {"ok": True}