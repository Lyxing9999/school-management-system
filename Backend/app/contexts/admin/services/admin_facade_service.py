from pymongo.database import Database
from app.contexts.admin.services.user_service import UserAdminService
from app.contexts.admin.services.staff_service import StaffAdminService
from app.contexts.admin.services.class_service import ClassAdminService
from app.contexts.admin.services.subject_service import SubjectAdminService
from app.contexts.admin.error.admin_exception import EmailAlreadyExistsException
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO
from app.contexts.iam.domain.iam import IAM
from app.contexts.staff.domain import Staff
from app.contexts.staff.data_transfer.requests import StaffCreateSchema
from app.contexts.admin.services.schedule_service import ScheduleAdminService
from typing import Tuple

class AdminFacadeService:
    def __init__(self, db: Database):
        self.user_service = UserAdminService(db)
        self.staff_service = StaffAdminService(db)
        self.class_service = ClassAdminService(db)
        self.subject_service = SubjectAdminService(db)
        self.schedule_service = ScheduleAdminService(db)



    # ---------- helper methods ----------
    def _rollback(self, user: IAMBaseDataDTO | None, staff: Staff | None):
        try:
            if staff:
                self.staff_service.admin_hard_delete_staff(staff.id)
        except Exception as e:
            pass
        try:
            if user:
                self.user_service.admin_hard_delete_user(user.id)
        except Exception as e:
            pass


    def admin_create_staff_workflow(self, payload, created_by) -> Tuple[IAM, Staff]:
        """
        Full workflow: create a user + linked staff record.
        """
        user = None
        staff = None
        try:
            user = self.user_service.admin_create_user(payload=payload, created_by=created_by)
            staff_payload = StaffCreateSchema(
                staff_id=payload.staff_id,      
                staff_name=payload.staff_name,    
                role=payload.role,
                phone_number=getattr(payload, "phone_number", None),
                address=getattr(payload, "address", None),
                user_id=user.id,              
                created_by=created_by
            )

            staff = self.staff_service.admin_create_staff(
                payload=staff_payload,
                created_by=created_by,
                user_id=user.id
            )
            return user, staff

        except EmailAlreadyExistsException as e:
            self._rollback(user, staff)
            raise
        except Exception as e:
            self._rollback(user, staff)
            raise

