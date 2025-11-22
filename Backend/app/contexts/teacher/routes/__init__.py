from flask import Blueprint, g
from app.contexts.infra.database.db import get_db
from app.contexts.teacher.services.teacher_service import TeacherService

teacher_bp = Blueprint("teacher", __name__)

@teacher_bp.before_app_request
def inject_teacher_service():
    if not hasattr(g, "teacher_service"):
        g.teacher_service = TeacherService(get_db())


def register_routes():
    from . import teacher_route