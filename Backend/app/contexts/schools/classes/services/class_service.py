# app/contexts/school/services/class_service.py
from pymongo.database import Database
from app.contexts.shared.model_converter import mongo_converter
from bson import ObjectId
from app.contexts.schools.classes.data_transfer.requests import ClassCreateRequestSchema
from typing import Literal, List
from app.contexts.schools.classes.data_transfer.responses import ClassReadDataDTO
from app.contexts.schools.classes.error.school_exceptions import ClassCreateException
from app.contexts.schools.classes.repositories.class_repo import ClassRepository
from app.contexts.schools.classes.read_models.class_read_model import ReadClassModel
from app.contexts.schools.classes.models.school_class import SchoolClass, SchoolClassMapper, SchoolClassFactory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# -------------------------
# Class Service
# -------------------------
class ClassService:
    def __init__(self, db: Database):
        self.db = db
        self._school_class_mapper = SchoolClassMapper()
        self._school_class_factory = SchoolClassFactory()

    def _log(self, operation: str, class_id: str | None = None, extra: dict | None = None):
        msg = f"ClassService::{operation}"
        if class_id:
            msg += f" [class_id={class_id}]"
        logger.info(msg, extra=extra or {})

    @property
    def class_repo(self) -> ClassRepository:
        return ClassRepository(self.db)

    @property
    def class_read_model(self) -> ReadClassModel:
        return ReadClassModel(self.db)

    # -------------------------
    # Helper: Get domain class
    # -------------------------
    def get_class(self, class_id: str | ObjectId) -> SchoolClass:
        class_model = self.class_repo.find_by_id(mongo_converter.convert_to_object_id(class_id))
        return self._school_class_mapper.to_domain(class_model)

    # -------------------------
    # Create Class
    # -------------------------
    def class_create(self, payload: ClassCreateRequestSchema, owner_id: ObjectId, created_by: ObjectId) -> SchoolClass:
        class_model = self._school_class_factory.create_from_payload(payload, owner_id=owner_id, created_by=created_by)
        class_id = self.class_repo.save(self._school_class_mapper.to_persistence_dict(class_model))
        if not class_id:
            raise ClassCreateException(class_id)
        class_model.id = class_id

        return class_model

    # -------------------------
    # Generic field modifier
    # -------------------------
    def _modify_field(self, class_id: str | ObjectId, field: str, values: str | List[str], action: Literal["assign", "remove"], domain_update=None) -> SchoolClass:
        class_obj = self.get_class(class_id)
        class_id_obj = mongo_converter.convert_to_object_id(class_id)

        if isinstance(values, str):
            values_list = [values]
        else:
            values_list = values

        if domain_update:
            domain_update(class_obj, values_list, action)

        if action == "assign":
            self.class_repo.add_to_set(class_id_obj, field, values_list)
        elif action == "remove":
            self.class_repo.pull_from_set(class_id_obj, field, values_list)

        return class_obj

    # -------------------------
    # Modify teacher
    # -------------------------
    def modify_teacher(self, class_id: str | ObjectId, teacher_id: str | ObjectId, action: Literal["assign", "remove"]) -> SchoolClass:
        def domain_update(obj, vals, act):
            obj.homeroom_teacher = vals[0] if act == "assign" else None
        return self._modify_field(class_id, "homeroom_teacher", teacher_id, action, domain_update)

    # -------------------------
    # Modify student
    # -------------------------
    def modify_student(self, class_id: str | ObjectId, student_id: str | ObjectId, action: Literal["assign", "remove"]) -> SchoolClass:
        def domain_update(obj, vals, act):
            for val in vals:
                if act == "assign":
                    obj.add_student(val)
                else:
                    obj.remove_student(val)

        return self._modify_field(class_id, "students", student_id, action, domain_update)

    # -------------------------
    # Modify subject
    # -------------------------
    def modify_subject(self, class_id: str | ObjectId, subjects: List[str], action: Literal["assign", "remove"]) -> SchoolClass:
        def domain_update(obj, vals, act):
            for val in vals:
                if act == "assign":
                    obj.add_subject(val)
                else:
                    obj.remove_subject(val)

        return self._modify_field(class_id, "subjects", subjects, action, domain_update)

    # -------------------------
    # Soft delete class
    # -------------------------
    def soft_delete(self, class_id: str | ObjectId) -> ClassReadDataDTO:
        self.class_repo.soft_delete(mongo_converter.convert_to_object_id(class_id))
        updated_doc = self.class_read_model.get_by_id_dto(class_id)
        self._log("soft_delete", class_id=str(class_id))
        return updated_doc