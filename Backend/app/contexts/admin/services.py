
from pymongo.database import Database
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.iam.data_transfer.responses import UserReadDataDTO
from app.contexts.schools.classes.models.school_class import SchoolClass
from app.contexts.admin.data_transfer.requests import AdminCreateClassSchema , AdminCreateUserSchema
from typing import Tuple , List
from app.contexts.admin.data_transfer.requests import AdminUpdateUserSchema
from app.contexts.iam.models import User
from app.contexts.admin.data_transfer.responses import   AdminStaffSelectDataDTO
from app.contexts.admin.error.admin_exceptions import StaffNotFoundException 
from app.contexts.admin.error.admin_exceptions import NoChangeAppException
from app.contexts.schools.classes.services.class_service import ClassService
from app.contexts.iam.read_models import UserReadModel
from app.contexts.iam.services import IAMService
from app.contexts.staff.read_models import StaffReadModel
from app.contexts.shared.enum.roles import SystemRole
from app.contexts.schools.classes.models.school_class import SchoolClass , SchoolClassMapper , SchoolClassFactory
from bson import ObjectId

class AdminService:
    def __init__(self, db: Database):
        self.db = db
        self._class_service = None
        self._user_read_model = None
        self._iam_service = None
        self._staff_read_model = None

    # -------- Lazy loaded services --------
    @property
    def class_service(self) -> ClassService:
        if self._class_service is None:
            self._class_service = ClassService(self.db)
        return self._class_service

    @property
    def user_read_model(self) -> UserReadModel:
        if self._user_read_model is None:
            self._user_read_model = UserReadModel(self.db)
        return self._user_read_model

    @property
    def iam_service(self) -> IAMService:
        if self._iam_service is None:
            self._iam_service = IAMService(self.db)
        return self._iam_service

    @property
    def staff_read_model(self) -> StaffReadModel:
        if self._staff_read_model is None:
            self._staff_read_model = StaffReadModel(self.db)
        return self._staff_read_model
 


    def admin_create_user(self, payload: AdminCreateUserSchema, created_by: ObjectId | str) -> User:
        payload.created_by = mongo_converter.convert_to_object_id(created_by)
        return self._iam_service.register_user(payload , trusted_by_admin=True)


    def admin_update_user(self, user_id: str | ObjectId, payload: AdminUpdateUserSchema) -> User:
        return self._iam_service.update_profile(mongo_converter.convert_to_object_id(user_id), payload)


    def admin_delete_user(self, user_id: str | ObjectId) -> bool:
        user: User = self._iam_service.delete_user(mongo_converter.convert_to_object_id(user_id))
        if user.is_deleted():
            raise NoChangeAppException()
        return True


    def admin_get_users(self, role: SystemRole,  page: int, page_size: int) -> Tuple[List[UserReadDataDTO], int]:
        cursor , total = self.user_read_model.get_page_by_role(role, page=page, page_size=page_size)
        users = mongo_converter.cursor_to_dto(cursor, UserReadDataDTO)
        return users , total




    def admin_create_class(self, payload: AdminCreateClassSchema, created_by: str | ObjectId) -> dict:
        created_by = mongo_converter.convert_to_object_id(created_by)
        owner_id = mongo_converter.convert_to_object_id(payload.owner_id)
        school_class_model = self.class_service.class_create(payload, owner_id=owner_id, created_by=created_by)
        owner_name = self.staff_read_model.get_staff_username_by_id(owner_id)
        safe_dict = SchoolClassMapper.to_safe_dict(school_class_model)
        safe_dict["owner"] = owner_name
        return safe_dict



    def admin_get_academic_staff_for_select(self) -> List[AdminStaffSelectDataDTO]:
        academic_staff_list = self.staff_read_model.get_staff_by_role_for_select("teacher")
        if not academic_staff_list:
            raise StaffNotFoundException("teacher")
        student_list = academic_staff_list.get("students")
        academic_staff = mongo_converter.cursor_to_dto(academic_staff_list, AdminStaffSelectDataDTO)

        return academic_staff