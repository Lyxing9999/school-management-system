from pymongo.database import Database
from bson import ObjectId
from typing import List, Optional
from app.contexts.shared.model_converter import  mongo_converter
from app.contexts.schools.services.class_service import ClassService
from app.contexts.admin.data_transfer.request import (
    AdminCreateClassSchema,
    AdminUpdateClassSchema,
)

from app.contexts.core.log.log_service import LogService
from app.contexts.schools.models.school_class import SchoolClassBaseDataDTO
class ClassAdminService:
    def __init__(self, db: Database):
        self.db = db
        self._class_service: Optional[ClassService] = None
        self._log_service: Optional[LogService] = None
        self.class_collection = self.db["classes"]


    @property
    def class_service(self) -> ClassService:
        if self._class_service is None:
            self._class_service = ClassService(self.db)
        return self._class_service

    def _convert_id(self, id: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_ids(id)

    def admin_get_class_by_id(self, class_id: str) -> SchoolClassBaseDataDTO:
        """Fetch a single class by ID."""
        return self.class_service.find_class_by_id_dto(class_id)

    def admin_get_classes(self) -> List[SchoolClassBaseDataDTO]:
        """Fetch all classes."""
        return self.class_service.find_all_classes_dto()
    def admin_create_class( self, payload: AdminCreateClassSchema, created_by: str | ObjectId ) -> SchoolClassBaseDataDTO:
        created_by_obj = self._convert_id(created_by)
        return self.class_service.create_class(payload, created_by_obj)
    def admin_update_class( self, class_id: str | ObjectId, payload: AdminUpdateClassSchema ) -> SchoolClassBaseDataDTO:
        class_id_obj = self._convert_id(class_id)
        return self.class_service.update_class(class_id_obj, payload)

    def admin_soft_delete_class( self, class_id: str | ObjectId, deleted_by: str | ObjectId ) -> bool:
        class_id_obj = self._convert_id(class_id)
        deleted = self.class_service.soft_delete(class_id_obj)
        return bool(deleted)
    def admin_assign_teacher( self, class_id: str | ObjectId, teacher_id: str | ObjectId ) -> SchoolClassBaseDataDTO:
        class_id_obj = self._convert_id(class_id)
        return self.class_service.modify_teacher(class_id_obj, teacher_id)
    def admin_assign_student( self, class_id: str | ObjectId, student_id: str | ObjectId ) -> SchoolClassBaseDataDTO:
        class_id_obj = self._convert_id(class_id)
        return self.class_service.modify_student(class_id_obj, student_id, action="assign")
    def admin_remove_student( self, class_id: str | ObjectId, student_id: str | ObjectId ) -> SchoolClassBaseDataDTO:
        class_id_obj = self._convert_id(class_id)
        return self.class_service.modify_student(class_id_obj, student_id, action="remove")
    def admin_change_class_room( self, class_id: str | ObjectId, new_room: str ) -> SchoolClassBaseDataDTO:
        class_id_obj = self._convert_id(class_id)
        return self.class_service.modify_class_room(class_id_obj, new_room)
