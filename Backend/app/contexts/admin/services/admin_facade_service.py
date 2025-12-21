from pymongo.database import Database
from typing import Tuple
from bson import ObjectId

# Imports DTOs/Schemas
from app.contexts.admin.data_transfer.requests import (
    AdminCreateStudentSchema,
    AdminCreateUserSchema

)
from app.contexts.staff.data_transfer.requests import StaffCreateSchema
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO
# Imports Services
from app.contexts.admin.services.user_service import UserAdminService
from app.contexts.admin.services.staff_service import StaffAdminService
from app.contexts.admin.services.class_service import ClassAdminService
from app.contexts.admin.services.subject_service import SubjectAdminService
from app.contexts.admin.services.schedule_service import ScheduleAdminService
from app.contexts.admin.services.student_service import StudentAdminService 

# Imports Read Models & Domain
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
from app.contexts.iam.domain.iam import IAM
from app.contexts.staff.domain.staff import Staff

# Imports Errors & Utils
from app.contexts.admin.error.admin_exception import CannotDeleteUserInUseException
from app.contexts.shared.model_converter import mongo_converter

class AdminFacadeService:
    def __init__(self, db: Database):
        self.user_service = UserAdminService(db)
        self.staff_service = StaffAdminService(db)
        self.class_service = ClassAdminService(db)
        self.subject_service = SubjectAdminService(db)
        self.schedule_service = ScheduleAdminService(db)
        self.student_service = StudentAdminService(db)
        self.admin_read_model = AdminReadModel(db)

    # ---------- helper methods ----------
    def _rollback(self, user: IAMBaseDataDTO | None, staff: Staff | None):
        try:
            if staff:
                self.staff_service.admin_hard_delete_staff(staff.id)
        except Exception:
            pass
        try:
            if user:
                self.user_service._rollback_purge_user(user.id)
        except Exception:
            pass

    # ---------- STAFF WORKFLOW ----------
    def admin_create_staff_workflow(self, payload, created_by) -> Tuple[IAM, Staff]:
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

        except Exception as e:
            self._rollback(user, staff)
            raise


    # ---------- STUDENT WORKFLOW (COMPLETED) ----------
    def admin_create_student_workflow(
        self, 
        payload: AdminCreateStudentSchema, 
        created_by: str | ObjectId
    ) -> dict:
        """
        1. Create IAM User (Login)
        2. Create Student Profile (Data)
        3. If Profile fails -> Rollback (Delete User)
        """
        user = None
        try:
            # 1. CREATE IAM USER FIRST
            # We extract only the Account fields from the big payload
            user_input = AdminCreateUserSchema(
                email=payload.email,
                password=payload.password,
                username=payload.username,
                role="student" 
            )
            
            # This returns the created User Domain Object (with .id)
            user = self.user_service.admin_create_user(user_input, created_by) 

            # 2. CREATE STUDENT PROFILE
            # We pass the full payload (containing DOB, names, etc.)
            # And explicitly pass the new user.id to link them together
            student = self.student_service.admin_create_student_profile(
                payload=payload, 
                user_id=user.id,
                created_by=created_by
            )

            return {
                "user": user,
                "student": student
            }

        except Exception as e:
            # 3. ROLLBACK STRATEGY
            # If Profile creation fails (e.g. duplicate student ID), 
            # we must delete the User we just created to avoid orphan accounts.
            if user:
                self.user_service._rollback_purge_user(user.id)
            raise e