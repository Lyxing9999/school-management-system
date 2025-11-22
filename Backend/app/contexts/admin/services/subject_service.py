from __future__ import annotations
from typing import Optional

from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.domain.subject import Subject
from app.contexts.admin.data_transfer.request import AdminCreateSubjectSchema
from app.contexts.admin.mapper.school_admin_mapper import SchoolAdminMapper
from app.contexts.admin.data_transfer.response import AdminSubjectDataDTO
from app.contexts.shared.decorators.logging_decorator import log_operation


class SubjectAdminService:
    """
    Admin-facing application service for Subject management.
    Delegates domain rules to SchoolService + SubjectFactory.
    """

    def __init__(self, db: Database):
        self.school_service = SchoolService(db)

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

    def admin_get_subject(self, subject_id: str) -> Subject:
        return self.school_service.get_subject_by_id(subject_id)


    @log_operation(level="INFO")
    def admin_deactivate_subject(self, subject_id: str) -> Optional[Subject]:
        return self.school_service.deactivate_subject(subject_id)

    @log_operation(level="INFO")
    def admin_activate_subject(self, subject_id: str) -> Optional[Subject]:
        return self.school_service.activate_subject(subject_id)