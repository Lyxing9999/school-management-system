from __future__ import annotations
from typing import Optional

from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.domain.subject import Subject
from app.contexts.admin.data_transfer.request import AdminCreateSubjectSchema
from app.contexts.shared.decorators.logging_decorator import log_operation


from app.contexts.school.read_models.subject_read_model import SubjectReadModel

class SubjectAdminService:
    """
    Admin-facing application service for Subject management.
    Delegates domain rules to SchoolService + SubjectFactory.
    """

    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        self.subject_read = SubjectReadModel(db)
    @log_operation(level="INFO")
    def admin_create_subject(
        self,
        payload: AdminCreateSubjectSchema,
        created_by: str | ObjectId,  
    ) -> Subject:
        subject = self.school_service.create_subject(
            name=payload.name,
            code=payload.code,
            description=payload.description,
            allowed_grade_levels=payload.allowed_grade_levels,
        )
        return subject



    @log_operation(level="INFO")
    def admin_deactivate_subject(self, subject_id: str) -> Optional[Subject]:
        return self.school_service.deactivate_subject(subject_id)

    @log_operation(level="INFO")
    def admin_activate_subject(self, subject_id: str) -> Optional[Subject]:
        return self.school_service.activate_subject(subject_id)


    def admin_get_subject(self, subject_id: str) -> Subject:
        return self.subject_read.get_by_id(subject_id)

    def admin_list_subject(self) -> list[Subject]:
        return self.subject_read.list_all()
        
    def admin_list_subject_name_select(self) -> list[Subject]:
        return self.subject_read.list_all_name_select()