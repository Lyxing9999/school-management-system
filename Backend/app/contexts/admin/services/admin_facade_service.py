from pymongo.database import Database
from app.contexts.admin.services.user_service import UserAdminService
from app.contexts.admin.services.staff_service import StaffAdminService
from app.contexts.admin.services.student_service import StudentAdminService
from app.contexts.admin.services.class_service import ClassAdminService
from app.contexts.admin.services.subject_service import SubjectAdminService
from app.contexts.admin.error.admin_exceptions import EmailAlreadyExistsException
from app.contexts.iam.data_transfer.responses import IAMBaseDataDTO
from app.contexts.staff.models import Staff
from app.contexts.staff.data_transfer.requests import StaffCreateSchema

class AdminFacadeService:
    def __init__(self, db: Database):
        self.user_service = UserAdminService(db)
        self.staff_service = StaffAdminService(db)
        self.student_service = StudentAdminService(db)
        self.class_service = ClassAdminService(db)
        self.subject_service = SubjectAdminService(db)


    def _rollback(self, user: IAMBaseDataDTO | None, staff: Staff | None):
        """Rollback created user/staff on failure."""
        if staff:
            self.staff_service.admin_hard_delete_staff(staff.id)
        if user:
            self.user_service.admin_hard_delete_user(user.id)



    def admin_create_staff_workflow(self, payload, created_by):
        """
        Full workflow: create a user + linked staff record.
        """
        user = None
        staff = None
        try:
            user = self.user_service.admin_create_user(payload=payload, created_by=created_by)
            staff_payload = StaffCreateSchema(
                staff_id=payload.staff_id,      
                staff_name=payload.username,    
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

    def admin_assign_student_to_class(self, student_id, class_id):
        """
        Example cross-service workflow: assign student to a class.
        """
        student = self.student_service.admin_get_student_by_user_id(student_id)
        updated_class = self.class_service.admin_assign_student(class_id, student)

        return updated_class