from pymongo.database import Database
from app.contexts.admin.read_models import AdminReadModel
from typing import Tuple , List
from app.contexts.shared.enum.roles import UserRole
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.academic.data_transfer.responses import AcademicUserDataDTO , AcademicFindAllClassDataDTO , AcademicFindAllClassDataDTOList , AcademicStaffNameSelectDTO
from app.contexts.academic.data_transfer.requests import AcademicCreateClassSchema
from app.contexts.schools.classes.services.class_service import ClassService
from app.contexts.academic.read_models import academic_read_model
class AcademicService:
    def __init__(self, db: Database):
        self._db = db
        self._admin_read_model = AdminReadModel(db)
        self._class_service = None
        self._academic_read_model = None

    @property
    def class_service(self) -> ClassService:
        if self._class_service is None:
            self._class_service = ClassService(self._db)
        return self._class_service

    @property
    def academic_read_model(self) -> academic_read_model:
        if self._academic_read_model is None:
            self._academic_read_model = academic_read_model(self._db)
        return self._academic_read_model
    
    def academic_get_students_page(self, page: int = 1, page_size: int = 5) -> Tuple[List[dict], int]:
        users_cursor, total = self._admin_read_model.get_page_by_role(UserRole.STUDENT.value, page, page_size)
        users_dto = mongo_converter.cursor_to_dto(users_cursor, AcademicUserDataDTO)
        
        return users_dto, total



    def academic_get_all_classes(self) -> AcademicFindAllClassDataDTOList:
        raw_classes = self.academic_read_model.get_all_classes()
        return mongo_converter.cursor_to_dto(raw_classes, AcademicFindAllClassDataDTO)

    def academic_create_class(self, class_create_schema: AcademicCreateClassSchema, created_by: str) -> dict:
        return self.class_service.create_class(class_create_schema, created_by)
      


    def academic_get_staff_name_select(self, search_text: str = "") -> AcademicStaffNameSelectDTO:
        raw = self.academic_read_model.get_staff_name_select(search_text)
        return mongo_converter.cursor_to_dto(raw, AcademicStaffNameSelectDTO)

    
    def academic_list_teacher_names(self) -> list[dict]:
        raw = self.academic_read_model.list_teacher_names()
        return mongo_converter.cursor_to_dto(raw, AcademicStaffNameSelectDTO)
        