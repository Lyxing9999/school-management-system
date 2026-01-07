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

from app.contexts.admin.features.dashboard.dashboard_read_model import AdminDashboardReadModel
from app.contexts.admin.services.student_service import StudentAdminService
from app.contexts.admin.services.teaching_assignment_admin_service import TeachingAssignmentAdminService


from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.student.read_models.student_read_model import StudentReadModel
from app.contexts.shared.services.display_name_service import DisplayNameService


admin_bp = Blueprint("admin", __name__)


class AdminContext:
    """
    All admin-related services for the current request.
    """

    def __init__(self, db: Database) -> None:
        # -------------------------
        # Read models (shared)
        # -------------------------
        iam_read = IAMReadModel(db)
        staff_read = StaffReadModel(db)
        class_read = ClassReadModel(db)
        subject_read = SubjectReadModel(db)
        student_read = StudentReadModel(db)

        self.display = DisplayNameService(
            iam_read_model=iam_read,
            staff_read_model=staff_read,
            class_read_model=class_read,
            subject_read_model=subject_read,
            student_read_model=student_read,
        )

        # -------------------------
        # Admin services
        # -------------------------
        self.class_service = ClassAdminService(db)
        self.subject_service = SubjectAdminService(db)
        self.schedule_service = ScheduleAdminService(db)
        self.staff_service = StaffAdminService(db)
        self.facade = AdminFacadeService(db)
        self.user_service = UserAdminService(db)
        self.admin_read_model = AdminReadModel(db)
        self.dashboard_read_model = AdminDashboardReadModel(db)
        self.student_service = StudentAdminService(db)


        self.teaching_assignment_service = TeachingAssignmentAdminService(
            db,
            display=self.display,
        )


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
    from . import (
        class_route,
        staff_route,
        subject_route,
        schedule_route,
        user_route,
        dashboard_route,
        student_routes,
        teaching_assignment_route,
    )