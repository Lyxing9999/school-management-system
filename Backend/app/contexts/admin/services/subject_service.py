from typing import Optional, Tuple, List, Dict, Any
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.legacy.school_service import SchoolService
from app.contexts.school.domain.subject import Subject
from app.contexts.admin.data_transfer.requests import AdminCreateSubjectSchema
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.shared.lifecycle.filters import FIELDS
class SubjectAdminService:
    """
    Admin-facing application service for Subject management.
    Delegates domain rules to SchoolService + SubjectFactory.
    """

    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        self.subject_read = SubjectReadModel(db)

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


    def admin_update_subject_patch(self, subject_id: str, patch_data: dict) -> Optional[Subject]:
        return self.school_service.update_subject_patch(subject_id, **patch_data)


    def admin_soft_delete_subject(self, subject_id: str, actor_id: str | ObjectId) -> bool:
        return self.school_service.soft_delete_subject(subject_id, actor_id)

    def admin_restore_subject(self, subject_id: str) -> Optional[Subject]:
        return self.school_service.restore_subject(subject_id)

    def admin_deactivate_subject(self, subject_id: str) -> Optional[Subject]:
        return self.school_service.deactivate_subject(subject_id)


    def admin_activate_subject(self, subject_id: str) -> Optional[Subject]:
        return self.school_service.activate_subject(subject_id)


    def admin_get_subject(self, subject_id: str) -> Subject:
        return self.subject_read.get_by_id(subject_id)

    def admin_list_subjects(
        self,
        *,
        status: str,
        page: int,
        page_size: int,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        extra: Dict[str, Any] = {}

        # status filter
        if status == "active":
            extra["is_active"] = True
        elif status == "inactive":
            extra["is_active"] = False
        # else: "all" => no filter

        # search filter (optional)
        if search:
            s = search.strip()
            if s:
                extra["$or"] = [
                    {"name": {"$regex": s, "$options": "i"}},
                    {"code": {"$regex": s, "$options": "i"}},
                    # add more fields if needed:
                    # {"description": {"$regex": s, "$options": "i"}},
                ]

        return self.subject_read.list_paginated(
            extra=extra,
            page=page,
            page_size=page_size,
            show_deleted="active",
            sort=[(FIELDS.k(FIELDS.created_at), -1)],
        )

    def admin_list_subject_name_select(self) -> list[Subject]:
        return self.subject_read.list_all_name_select()