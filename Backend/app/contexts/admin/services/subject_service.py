from typing import List, Optional
from app.contexts.admin.data_transfer.request import (
    AdminCreateSubjectSchema,
    AdminUpdateSubjectSchema
)
from app.contexts.schools.models.school_class import SchoolClassBaseDataDTO
from app.contexts.schools.services.subject_service import SubjectService
from app.contexts.schools.data_transfer.responses.subject_responses import SubjectBaseDataDTO
from bson import ObjectId
from pymongo.database import Database
class SubjectAdminService:
    def __init__(self, db: Database):
        self.db = db
        self._subject_service: Optional[SubjectService] = None
        self.subject_collection = self.db["subjects"]
    def _convert_id(self, id: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_ids(id)

    @property
    def subject_service(self) -> SubjectService:
        if self._subject_service is None:
            self._subject_service = SubjectService(self.db)
        return self._subject_service

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
