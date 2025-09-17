
from pymongo.database import Database
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.iam.data_transfer.responses import UserReadDataDTO
from app.contexts.schools.classes.models.school_class import SchoolClass
from app.contexts.admin.data_transfer.requests import AdminCreateClassSchema , AdminCreateUserSchema
from typing import Tuple , List , Union
from app.contexts.admin.data_transfer.requests import AdminUpdateUserSchema
from app.contexts.iam.models import User 
from app.contexts.admin.data_transfer.responses import   AdminStaffSelectDataDTO
from app.contexts.admin.error.admin_exceptions import StaffNotFoundException 
from app.contexts.admin.error.admin_exceptions import NoChangeAppException
from app.contexts.schools.classes.services.class_service import ClassService
from app.contexts.iam.services import IAMService
from app.contexts.shared.enum.roles import SystemRole
from app.contexts.staff.services import StaffService
from app.contexts.admin.read_models import AdminReadModel
from app.contexts.staff.models import Staff, StaffMapper
from bson import ObjectId

class AdminService:
    def __init__(self, db: Database):
        self.db = db
        self._class_service = None
        self._iam_service = None
        self._staff_service = None
        self._admin_read_model = None

    # -------- Lazy loaded services --------
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


    # -------------------------
    # Manage users CRUD
    # -------------------------
    def admin_create_user(self, payload: AdminCreateUserSchema, created_by: ObjectId | str) -> User:
        created_by = mongo_converter.convert_to_object_id(created_by)
        payload.created_by = created_by
        user_model, token = self.iam_service.register_user(payload , trusted_by_admin=True)
        return user_model


    def admin_update_user(self, user_id: str | ObjectId, payload: AdminUpdateUserSchema) -> dict:
        user_model = self.iam_service.update_profile(mongo_converter.convert_to_object_id(user_id), payload)
        return self.iam_service.to_safe_dict(user_model)


    def admin_soft_delete_user(self, user_id: str | ObjectId) -> User:
        return self.iam_service.soft_delete(mongo_converter.convert_to_object_id(user_id))

    def admin_hard_delete_user(self, user_id: str | ObjectId) -> bool:
        return self.iam_service.hard_delete(mongo_converter.convert_to_object_id(user_id))

    def admin_get_users(self, role:  Union[str, list[str]],  page: int, page_size: int) -> Tuple[List[UserReadDataDTO], int]:
        cursor , total = self.admin_read_model.get_page_by_role(role, page=page, page_size=page_size)
        users = mongo_converter.cursor_to_dto(cursor, UserReadDataDTO)
        return users , total




    # -------------------------
    # Manage classes 
    # -------------------------
    def admin_create_class(self, payload: AdminCreateClassSchema, created_by: str | ObjectId) -> dict:
        created_by = mongo_converter.convert_to_object_id(created_by)
        owner_id = mongo_converter.convert_to_object_id(payload.owner_id)
        school_class_model = self.class_service.class_create(payload, owner_id=owner_id, created_by=created_by)
        owner_name = self.staff_read_model.get_staff_username_by_id(owner_id)
        safe_dict = SchoolClassMapper.to_safe_dict(school_class_model)
        safe_dict["owner"] = owner_name
        return safe_dict



    # Task to Day
    # def admin_get_classes(self, role:  Union[str, list[str]],  page: int, page_size: int) -> Tuple[List[SchoolClassReadDataDTO], int]:
    #     pass


    # -------------------------
    # Manage staff 
    # -------------------------
    def admin_create_staff(self, payload: AdminCreateUserSchema, created_by: str | ObjectId) -> tuple[User, Staff]:
        created_by = mongo_converter.convert_to_object_id(created_by)
        user_model = None
        staff_model = None
        try:
            user_model = self.admin_create_user(payload, created_by)
            staff_model = self.staff_service.create_staff(payload, created_by)
            return user_model , staff_model
        except Exception as e:
            if staff_model:
                self.staff_service.admin_hard_delete_staff(staff_model.id)
            if user_model:
                self.admin_hard_delete_user(user_model.id)
            raise e

    def admin_update_staff(self, staff_id: str | ObjectId, payload: AdminUpdateUserSchema) -> tuple[User, Staff]:
        return self.staff_service.update_staff(staff_id, payload)

    def admin_soft_delete_staff(self, staff_id: str | ObjectId, deleted_by: ObjectId | str) -> bool:
        staff = self.staff_service.soft_staff_delete(staff_id, deleted_by)  # already soft-deletes
        self.admin_soft_delete_user(staff.user_id)  # soft-delete corresponding user
        return True

    def admin_hard_delete_staff(self, staff_id: str | ObjectId) -> bool:
        staff_model = self.staff_service.get_to_staff_domain(staff_id)
        if self.staff_service.hard_staff_delete(staff_id):
            self.admin_hard_delete_user(staff_model.user_id)
            return True
        return False



    # def admin_get_academic_staff_for_select(self) -> List[AdminStaffSelectDataDTO]:
    #     academic_staff_list = self.staff_read_model.get_staff_by_role_for_select("teacher")
    #     if not academic_staff_list:
    #         raise StaffNotFoundException("teacher")
    #     student_list = academic_staff_list.get("students")
    #     academic_staff = mongo_converter.cursor_to_dto(academic_staff_list, AdminStaffSelectDataDTO)

    #     return academic_staff