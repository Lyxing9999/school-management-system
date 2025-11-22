# app/contexts/admin/routes/__init__.py
from flask import Blueprint, g
from app.contexts.infra.database.db import get_db
from app.contexts.admin.services.admin_facade_service import AdminFacadeService

admin_bp = Blueprint("admin", __name__)

@admin_bp.before_app_request
def load_admin_facade():
    g.admin_facade = AdminFacadeService(get_db())


def register_routes():
    from . import user_routes, staff_route, class_routes, subject_routes, schedule_routes