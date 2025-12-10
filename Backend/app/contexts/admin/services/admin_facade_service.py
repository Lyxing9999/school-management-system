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
from typing import Tuple,Optional, Union
from bson import ObjectId
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
from app.contexts.admin.error.admin_exception import CannotDeleteUserInUseException
from app.contexts.shared.model_converter import mongo_converter

class AdminFacadeService:
    def __init__(self, db: Database):
        self.user_service = UserAdminService(db)
        self.staff_service = StaffAdminService(db)
        self.class_service = ClassAdminService(db)
        self.subject_service = SubjectAdminService(db)
        self.schedule_service = ScheduleAdminService(db)
        self.admin_read_model = AdminReadModel(db)



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

    


    def admin_soft_delete_user_workflow(
        self,
        user_id: Union[str, ObjectId],
        deleted_by: Union[str, ObjectId],
    ) -> Tuple[Optional[dict], Optional[dict]]:
        """
        Soft-delete a user only if it is safe (read-model based).

        Workflow:
        - Normalize user_id to ObjectId.
        - Load the user document by _id.
        - Load the related staff document by user_id.
        - Check if that staff is still referenced (schedules, classes, etc.).
        If yes, raise CannotDeleteUserInUseException instead of deleting.
        - If safe, soft-delete staff first, then user.
        - Return (user_doc, staff_doc) that were deleted (or None, None if not found).
        """

        # 0) Normalize ID once
        user_oid: ObjectId = mongo_converter.convert_to_object_id(user_id)

        # 1) Load user doc
        user_doc: Optional[dict] = self.admin_read_model.get_user_by_id(user_oid)
        if user_doc is None:
            # User does not exist; nothing to delete.
            return None, None

        # 2) Load staff doc by user_id (NOT by staff._id)
        #    Here your get_staff_by_user_id expects user_id (link from staff -> IAM)
        staff_doc: Optional[dict] = self.admin_read_model.get_staff_by_user_id(user_oid)

        # We will return the original docs (before delete) – sufficient for DTOs
        staff_deleted_doc: Optional[dict] = staff_doc
        user_deleted_doc: Optional[dict] = user_doc

        # 3) Check relationships before delete
        if staff_doc:
            # Decide what your schedule/class collections use as teacher_id.
            # Most schemas use staff._id as the teacher_id:
            teacher_id: ObjectId = staff_doc["_id"]

            schedule_count = self.schedule_service.admin_count_schedules_for_teacher(
                teacher_id
            )
            if schedule_count > 0:
                raise CannotDeleteUserInUseException("schedules", schedule_count)

            class_count = self.class_service.admin_count_classes_for_teacher(
                teacher_id
            )
            if class_count > 0:
                raise CannotDeleteUserInUseException("classes", class_count)

        # 4) Perform soft delete(s) in safe order: staff, then user
        if staff_doc:
            # staff_service expects staff_id, not user_id
            self.staff_service.admin_soft_delete_staff(
                user_oid,
                deleted_by,
            )

        # Only delete user if staff was successfully soft-deleted or no staff exists
        # (Here we assume admin_soft_delete_staff will raise on failure)
        self.user_service.admin_soft_delete_user(user_oid)

        return user_deleted_doc, staff_deleted_doc