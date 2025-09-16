from pymongo.database import Database
from app.contexts.schools.classes.services.class_service import ClassService
from app.contexts.schools.classes.models.school_class import SchoolClass
from app.contexts.staff.read_models import StaffReadModel
from app.contexts.shared.enum.roles import StaffRole
from app.contexts.academic.models import Academic
from app.contexts.academic.data_transfer.requests import AcademicAddSubjectSchema
from app.contexts.academic.error.academic_execptions import StaffRoleException
from app.contexts.schools.classes.repositories.class_repo import ClassRepository
from app.contexts.schools.classes.read_models.class_read_model import ReadClassModel
from typing import List , Any
from app.contexts.schools.classes.read_models.class_read_model import ReadClassModel
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.academic.data_transfer.responses import AcademicFindAllClassDataDTO
from bson import ObjectId

class AcademicService:
    def __init__(self, db: Database):
        self._class_service = ClassService(db)
        self._staff_read_model = StaffReadModel(db)
        self._read_class_model = ReadClassModel(db)


    def get_academic(self, academic_id: ObjectId) -> Academic: 
        academic = self._staff_read_model.get_staff(academic_id)
        if academic.role != StaffRole.ACADEMIC:
            raise StaffRoleException(f"Staff {academic_id} is not an academic")
        return AcademicMapper.to_domain(academic)


    def get_classes(self) -> List[AcademicFindAllClassDataDTO]:
        raw_dict = self._read_class_model.get_class()
        return mongo_converter.cursor_to_dto(raw_dict , AcademicFindAllClassDataDTO)