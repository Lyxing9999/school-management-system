# app/contexts/admin/routes/__init__.py
from flask import Blueprint, g
from pymongo.database import Database

from app.contexts.infra.database.db import get_db
from app.contexts.admin.services.admin_facade_service import AdminFacadeService
from app.contexts.admin.services.class_service import ClassAdminService
from app.contexts.admin.services.subject_service import SubjectAdminService
from app.contexts.admin.services.schedule_service import ScheduleAdminService
from app.contexts.admin.services.staff_service import StaffAdminService
from app.contexts.admin.services.user_service import UserAdminService
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
from app.contexts.admin.read_models.admin_dashboard_read_model import AdminDashboardReadModel
from app.contexts.admin.services.student_service import StudentAdminService
admin_bp = Blueprint("admin", __name__)


class AdminContext:
    """
    All admin-related services for the current request.

    - facade: cross-service workflows (e.g. create staff + user)
    - class_service: class CRUD
    - subject_service: subject CRUD
    - schedule_service: schedule CRUD
    - staff_service: staff CRUD
    - user_service: user CRUD
    """
    def __init__(self, db: Database) -> None:
        self.class_service = ClassAdminService(db)
        self.subject_service = SubjectAdminService(db)
        self.schedule_service = ScheduleAdminService(db)
        self.staff_service = StaffAdminService(db)
        self.facade = AdminFacadeService(db)
        self.user_service = UserAdminService(db)
        self.admin_read_model = AdminReadModel(db)
        self.dashboard_read_model = AdminDashboardReadModel(db)
        self.student_service = StudentAdminService(db)

@admin_bp.before_app_request
def load_admin_context() -> None:
    """
    Attach a single AdminContext to g for this request.
    """
    if not hasattr(g, "admin"):
        db = get_db()
        g.admin = AdminContext(db)

@admin_bp.teardown_app_request
def remove_admin_context(exc=None) -> None:
    if hasattr(g, "admin"):
        del g.admin

def register_routes():
    from . import class_route, staff_route, subject_route, schedule_route, user_route, dashboard_route, student_routes