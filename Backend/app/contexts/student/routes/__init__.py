# app/contexts/admin/routes/__init__.py
from flask import Blueprint, g
from app.contexts.infra.database.db import get_db
from app.contexts.student.services.student_service import StudentService

student_bp = Blueprint("student", __name__)


@student_bp.before_app_request
def inject_student_service():
    if not hasattr(g, "student_service"):
        g.student_service = StudentService(get_db())

def register_routes():
    from . import student_route