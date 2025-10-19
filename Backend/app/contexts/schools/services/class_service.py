# app/contexts/school/services/class_service.py
from pymongo.database import Database
from app.contexts.shared.model_converter import mongo_converter
from bson import ObjectId
from app.contexts.schools.data_transfer.requests.class_requests import SchoolClassCreateSchema, SchoolClassUpdateSchema
from typing import Literal, List
from app.contexts.schools.data_transfer.responses.class_responses import SchoolClassBaseDataDTO
from app.contexts.schools.error.school_exceptions import ClassCreateException
from app.contexts.schools.repositories.class_repo import ClassRepository
from app.contexts.schools.read_models.class_read_model import ClassReadModel
from app.contexts.schools.models.school_class import SchoolClass, SchoolClassMapper, SchoolClassFactory
from app.contexts.core.log.log_service import LogService
from time import time
# -------------------------
# Class Service
# -------------------------
class ClassService:
    def __init__(self, db: Database):
        self.db = db
        self._school_class_mapper = SchoolClassMapper()
        self._school_class_factory = SchoolClassFactory()
        self._class_repo = ClassRepository(self.db)
        self._class_read_model = ClassReadModel(self.db)
        self._log_service = LogService.get_instance() 

    def _log(self, operation: str, class_id: str | None = None, extra: dict | None = None, level: str = "INFO"):
        msg = f"ClassService::{operation}" + (f" [class_id={class_id}]" if class_id else "")
        self._log_service.log(msg, level=level, module="ClassService", extra=extra or {})

    # -------------------------
    # Helper: Get domain class
    # -------------------------
    def get_class_to_domain(self, class_id: str | ObjectId) -> SchoolClass:
        class_model = self._class_read_model.find_by_id(mongo_converter.convert_to_object_id(class_id))
        return self._school_class_mapper.to_domain(class_model)

    # -------------------------
    # Create Class
    # -------------------------
    def create_class(self, payload: SchoolClassCreateSchema, created_by: str) -> SchoolClassBaseDataDTO:
        created_by_obj_id = mongo_converter.convert_to_object_id(created_by)
        domain_class = self._school_class_factory.create_from_payload(payload)
        domain_class.created_by = created_by_obj_id
        saved_id = self._class_repo.save(self._school_class_mapper.to_persistence_dict(domain_class))
        if not saved_id:
            raise ClassCreateException(saved_id)
        domain_class.id = saved_id
        return self._school_class_mapper.to_dto(domain_class)

    def update_class(self, class_id: str | ObjectId, payload: SchoolClassUpdateSchema) -> SchoolClassBaseDataDTO:
        class_obj_id = mongo_converter.convert_to_object_id(class_id)
        school_class = self.get_class_to_domain(class_obj_id)
        school_class.update_info(
            name=payload.name,
            grade=payload.grade,
            max_students=payload.max_students,
            class_room=payload.class_room,
            status=payload.status,
            academic_year=payload.academic_year
        )
        
        self._class_repo.patch(class_obj_id, self._school_class_mapper.to_persistence_dict(school_class))
        return self._school_class_mapper.to_dto(school_class)
    
    # -------------------------
    # Generic field modifier
    # -------------------------
    def _modify_field(self, class_id: str | ObjectId, field: str, values: str | List[str], action: Literal["assign", "remove"], domain_update=None) -> SchoolClass:
        class_obj = self.get_class_to_domain(class_id)
        class_id_obj = mongo_converter.convert_to_object_id(class_id)

        if isinstance(values, str):
            values_list = [values]
        else:
            values_list = values

        if domain_update:
            domain_update(class_obj, values_list, action)

        if action == "assign":
            self._class_repo.add_to_set(class_id_obj, field, values_list)
        elif action == "remove":
            self._class_repo.pull_from_set(class_id_obj, field, values_list)

        return self._school_class_mapper.to_dto(class_obj)

    # -------------------------
    # Modify teacher
    # -------------------------
    def modify_teacher(self, class_id: str | ObjectId, teacher_id: str | ObjectId | None) -> SchoolClassBaseDataDTO:
        class_obj_id = mongo_converter.convert_to_object_id(class_id)
        class_obj = self.get_class_to_domain(class_obj_id)
        teacher_obj_id = (
            mongo_converter.convert_to_object_id(teacher_id)
            if teacher_id else None
        )
        class_obj.assign_teacher(teacher_obj_id)
        self._class_repo.update_field(class_obj_id, "homeroom_teacher", teacher_obj_id)
        return self._school_class_mapper.to_dto(class_obj)
    # -------------------------
    # Modify student
    # -------------------------
    def modify_student(self, class_id: str | ObjectId, student_id: str | ObjectId, action: Literal["assign", "remove"]) -> SchoolClassBaseDataDTO:
        class_obj_id = mongo_converter.convert_to_object_id(class_id)
        student_obj_id = mongo_converter.convert_to_object_id(student_id)
        def domain_update(obj, vals, act):
            for val in vals:
                if act == "assign":
                    obj.add_student(val)
                else:
                    obj.remove_student(val)

        return self._modify_field(class_obj_id, "students", student_obj_id, action, domain_update)

    # -------------------------
    # Modify class room
    # -------------------------
    def modify_class_room(self, class_id: str | ObjectId, class_room: str) -> SchoolClassBaseDataDTO:
        class_obj_id = mongo_converter.convert_to_object_id(class_id)
        class_obj = self.get_class_to_domain(class_obj_id)

        class_obj.change_classroom(class_room) 
        self._class_repo.update_field(class_obj_id, "class_room", class_room)

        return self._school_class_mapper.to_dto(class_obj)
    # -------------------------
    # Soft delete class
    # -------------------------
    def soft_delete(self, class_id: str | ObjectId) -> SchoolClassBaseDataDTO:
        self._class_repo.soft_delete(mongo_converter.convert_to_object_id(class_id))
        updated_doc = self._class_read_model.find_by_id(mongo_converter.convert_to_object_id(class_id))
        self._log("soft_delete", class_id=str(class_id))
        return self._school_class_mapper.to_dto(updated_doc)
    


    # -------------------------
    #  read class 
    # -------------------------
    def find_all_classes_dto(self) -> List[SchoolClassBaseDataDTO]:
        class_list = self._class_read_model.get_class()
        get_class_to_domain = [self._school_class_mapper.to_domain(c) for c in class_list]
        return [self._school_class_mapper.to_dto(c).model_dump() for c in get_class_to_domain]
    
    def find_class_by_id_dto(self, class_id: str | ObjectId) -> SchoolClassBaseDataDTO:
        class_obj = self._class_read_model.find_by_id(mongo_converter.convert_to_object_id(class_id))
        return self._school_class_mapper.to_dto(class_obj)