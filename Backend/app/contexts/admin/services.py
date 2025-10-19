from pymongo.database import Database
from bson import ObjectId
from typing import List, Tuple, Union, Optional

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.iam.models import IAMFactory , IAMMapper 
from app.contexts.iam.data_transfer.responses import IAMBaseDataDTO
from app.contexts.iam.services import IAMService
from app.contexts.staff.models import StaffMapper, Staff
from app.contexts.staff.services import StaffService
from app.contexts.student.services import StudentService
from app.contexts.schools.services.class_service import ClassService
from enum import Enum
from app.contexts.admin.read_models import AdminReadModel
from app.contexts.admin.data_transfer.requests import (
    AdminCreateUserSchema,
    AdminCreateStaffSchema,
    AdminCreateClassSchema,
    AdminUpdateUserSchema,
    AdminUpdateStaffSchema,
    AdminUpdateInfoStudentSchema,
    AdminUpdateClassSchema,
    AdminCreateSubjectSchema,
    AdminUpdateSubjectSchema
)

from app.contexts.admin.data_transfer.responses import AdminUpdateStaffDataDTO
from app.contexts.student.data_transfer.responses import StudentInfoBaseDataDTO
from app.contexts.staff.data_transfer.requests  import  StaffCreateSchema
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from app.contexts.admin.error.admin_exceptions import EmailAlreadyExistsException
from time import time
from app.contexts.shared.enum.roles import SystemRole 
from app.contexts.core.log.log_service import LogService
from app.contexts.schools.models.school_class import SchoolClassBaseDataDTO

from app.contexts.schools.services.subject_service import SubjectService
from app.contexts.schools.data_transfer.responses.subject_responses import SubjectBaseDataDTO
class AdminService:
    def __init__(self, db: Database):
        self.db = db
        self._class_service: Optional[ClassService] = None
        self._iam_service: Optional[IAMService] = None
        self._staff_service: Optional[StaffService] = None
        self._admin_read_model: Optional[AdminReadModel] = None
        self._student_service: Optional[StudentService] = None
        self._iam_factory: Optional[IAMFactory] = None
        self._staff_mapper: Optional[StaffMapper] = None
        self._log_service: Optional[LogService] = None
    # ------------------------- Lazy-loaded services -------------------------
    @property
    def class_service(self) -> ClassService:
        if self._class_service is None:
            self._class_service = ClassService(self.db)
        return self._class_service

    @property
    def iam_service(self) -> IAMService:
        if self._iam_service is None:
            self._iam_service = IAMService(self.db)
        return self._iam_service

    @property
    def staff_service(self) -> StaffService:
        if self._staff_service is None:
            self._staff_service = StaffService(self.db)
        return self._staff_service

    @property
    def admin_read_model(self) -> AdminReadModel:
        if self._admin_read_model is None:
            self._admin_read_model = AdminReadModel(self.db)
        return self._admin_read_model

    @property
    def student_service(self) -> StudentService:
        if self._student_service is None:
            self._student_service = StudentService(self.db)
        return self._student_service

    @property
    def iam_factory(self) -> IAMFactory:
        if self._iam_factory is None:
            self._iam_factory = IAMFactory(user_read_model=self.admin_read_model.iam_read_model)
        return self._iam_factory

    @property
    def staff_mapper(self) -> StaffMapper:
        if self._staff_mapper is None:
            self._staff_mapper = StaffMapper()
        return self._staff_mapper


    @property
    def subject_service(self) -> SubjectService:
        if self._subject_service is None:
            self._subject_service = SubjectService(self.db)
        return self._subject_service


    # ------------------------- Log service -------------------------
    def _log(self, operation: str, user_id: str | None = None, extra: dict | None = None, level: str = "INFO"):
        if self._log_service is None:
            self._log_service = LogService.get_instance()

        msg = f"AdminService::{operation}" + (f" [user_id={user_id}]" if user_id else "")
        self._log_service.log(
            msg,
            level=level,
            module="AdminService",
            user_id=user_id,
            extra=extra or {}
        )

    # ------------------------- Helper Methods -------------------------
    def _convert_id(self, obj_id: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(obj_id)

    def _rollback(self, user: IAMBaseDataDTO | None, staff: Staff | None):
        """Rollback created user/staff on failure."""
        if staff:
            self.staff_service.admin_hard_delete_staff(staff.id)
        if user:
            self.admin_hard_delete_user(user.id)

# =====================================================
# SECTION 1: USER MANAGEMENT (IAM)
# =====================================================
    def admin_create_user(self, payload: AdminCreateUserSchema, created_by: str | ObjectId) -> IAMBaseDataDTO:
        start = time()
        payload.created_by = self._convert_id(created_by)
        self._log("CreateUser - start", user_id=str(created_by), extra={"email": payload.email, "role": payload.role.value})
        iam_model = self.iam_factory.create_user(
            email=payload.email,
            password=payload.password,
            username=payload.username,
            role=payload.role,
            created_by=payload.created_by
        )
        iam_model = self.iam_service.save_domain(iam_model)
        duration_ms = (time() - start) * 1000
        self._log("CreateUser - end", user_id=str(created_by), extra={"email": payload.email, "role": payload.role.value, "duration_ms": duration_ms})
        return IAMMapper.to_dto(iam_model)


    def admin_update_user(
        self, user_id: str | ObjectId, payload: AdminUpdateUserSchema
    ) -> IAMBaseDataDTO:
        return self.iam_service.update_info(self._convert_id(user_id), payload, update_by_admin=True)

    def admin_soft_delete_user(self, user_id: str | ObjectId) -> IAMBaseDataDTO:
        return self.iam_service.soft_delete(self._convert_id(user_id))

    def admin_hard_delete_user(self, user_id: str | ObjectId) -> bool:
        return self.iam_service.hard_delete(self._convert_id(user_id))

    
    def admin_get_users(
        self, role: Union[str, list[str]], page: int, page_size: int
    ) -> Tuple[List[IAMBaseDataDTO], int]:
        start = time()
        cursor, total = self.admin_read_model.get_page_by_role(
            role, page=page, page_size=page_size
        )
        users = mongo_converter.cursor_to_dto(cursor, IAMBaseDataDTO)
        duration_ms = (time() - start) * 1000
        self._log("GetUsers - end", extra={"role": role, "page": page, "page_size": page_size, "duration_ms": duration_ms})
        return users, total

    # =====================================================
    # SECTION 2: STAFF MANAGEMENT
    # =====================================================
    def admin_create_staff( self, payload: AdminCreateStaffSchema, created_by: str ) -> Union[IAMBaseDataDTO, StaffBaseDataDTO]:
        
        user_obj = None
        staff_obj = None
        try:
            role = SystemRole(payload.role.value) if isinstance(payload.role, Enum) else SystemRole(payload.role)
            user_obj = self.admin_create_user(
                AdminCreateUserSchema(
                    email=payload.email,
                    username=payload.username,
                    password=payload.password,
                    role=role,
                ), created_by=created_by
            )
            user_id = self._convert_id(user_obj.id)
            payload.user_id = user_id
            if user_id:
                staff_obj = self.staff_service.create_staff(
                    StaffCreateSchema(
                        staff_id=payload.staff_id,
                        staff_name=payload.staff_name,
                        role=role,
                        phone_number=payload.phone_number,
                        address=payload.address
                    ),
                    created_by=created_by,
                    user_id=payload.user_id
                )
            user_dto = IAMMapper.to_dto(user_obj)
            staff_dto = StaffMapper.to_dto(staff_obj)
            return user_dto, staff_dto 
    
        except EmailAlreadyExistsException as e:
            self._rollback(user_obj, staff_obj)
            raise e
        except Exception as e:
            self._rollback(user_obj, staff_obj)
            raise
    def admin_update_staff( self, user_id: str | ObjectId, payload: AdminUpdateStaffSchema ) -> AdminUpdateStaffDataDTO:
        return self.staff_service.update_staff(user_id, payload)
    def admin_soft_delete_staff(self, staff_id: str | ObjectId, deleted_by: str | ObjectId) -> bool:
        staff = self.staff_service.soft_staff_delete(staff_id, deleted_by)
        self.admin_soft_delete_user(staff.user_id)
        return True
    def admin_hard_delete_staff(self, staff_id: str | ObjectId) -> bool:
        return self.staff_service.hard_staff_delete(staff_id)
    def admin_get_staff_by_id(self, staff_id: str) -> StaffBaseDataDTO:
        staff_domain:Staff =  self.staff_service.get_to_staff_domain(staff_id)
        return StaffMapper.to_dto(staff_domain)


    # =====================================================
    # SECTION 3: STUDENT MANAGEMENT
    # =====================================================
    def admin_get_student_by_user_id(self, user_id: str) -> StudentInfoBaseDataDTO:
        return self.student_service.get_student_info(user_id)

    def admin_update_student_info(self, user_id: str, student_payload: AdminUpdateInfoStudentSchema) -> StudentInfoBaseDataDTO:
        return self.student_service.save_student_info(user_id, student_payload)





    # =====================================================
    # SECTION 4: CLASS MANAGEMENT
    # =====================================================
    def admin_get_class_by_id(self, class_id: str) -> SchoolClassBaseDataDTO:
        """Fetch a single class by ID."""
        return self.class_service.find_class_by_id_dto(class_id)

    def admin_get_classes(self) -> List[SchoolClassBaseDataDTO]:
        """Fetch all classes."""
        return self.class_service.find_all_classes_dto()
    def admin_create_class( self, payload: AdminCreateClassSchema, created_by: str | ObjectId ) -> SchoolClassBaseDataDTO:
        created_by_obj = mongo_converter.convert_to_object_id(created_by)
        return self.class_service.create_class(payload, created_by_obj)
    def admin_update_class( self, class_id: str | ObjectId, payload: AdminUpdateClassSchema ) -> SchoolClassBaseDataDTO:
        return self.class_service.update_class(class_id, payload)

    def admin_soft_delete_class( self, class_id: str | ObjectId, deleted_by: str | ObjectId ) -> bool:
        deleted = self.class_service.soft_delete(class_id)
        return bool(deleted)
    def admin_assign_teacher( self, class_id: str | ObjectId, teacher_id: str | ObjectId ) -> SchoolClassBaseDataDTO:
        return self.class_service.modify_teacher(class_id, teacher_id)
    def admin_assign_student( self, class_id: str | ObjectId, student_id: str | ObjectId ) -> SchoolClassBaseDataDTO:
        return self.class_service.modify_student(class_id, student_id, action="assign")
    def admin_remove_student( self, class_id: str | ObjectId, student_id: str | ObjectId ) -> SchoolClassBaseDataDTO:
        return self.class_service.modify_student(class_id, student_id, action="remove")
    def admin_change_class_room( self, class_id: str | ObjectId, new_room: str ) -> SchoolClassBaseDataDTO:
        return self.class_service.modify_class_room(class_id, new_room)

    


    # =====================================================
    # SECTION 5: SUBJECT MANAGEMENT
    # =====================================================

    def admin_get_subject_by_id(self, subject_id: str) -> SubjectBaseDataDTO:
        return self.subject_service.find_subject_by_id_dto(subject_id)

    def admin_get_subjects(self) -> List[SubjectBaseDataDTO]:
        return self.subject_service.find_all_subjects_dto()
        
    def admin_create_subject(self, payload: AdminCreateSubjectSchema, created_by: str | ObjectId) -> SubjectBaseDataDTO:
        return self.subject_service.create_subject(payload, created_by)

    def admin_update_subject(self, subject_id: str | ObjectId, payload: AdminUpdateSubjectSchema) -> SubjectBaseDataDTO:
        return self.subject_service.update_subject(subject_id, payload)

    def remove_subject_from_class(self, class_id: str | ObjectId, subject_id: str | ObjectId) -> SchoolClassBaseDataDTO:
        return self.subject_service.remove_teacher_from_subject(class_id, subject_id)