from typing import Optional, List

from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.admin.data_transfer.requests import AdminCreateClassSchema
from app.contexts.admin.read_models.admin_read_model import AdminReadModel

class ClassAdminService:
    """
    Admin-facing application service for Class/Section management.

    - Commands (create/assign/enroll/unenroll/delete) go through SchoolService
      so domain rules are enforced.
    - Queries use ClassReadModel and return plain dicts optimized for reads.
    """

    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        self.class_read_model = ClassReadModel(db)
        self.admin_read_model = AdminReadModel(db)
    # ---------- Commands ----------

    def admin_create_class(
        self,
        payload: AdminCreateClassSchema,
        created_by: str | ObjectId,
    ) -> ClassSection:
        # SchoolService enforces:
        # - unique class name
        # - teacher max class load (inside ClassFactory / read models)
        return self.school_service.create_class(
            name=payload.name,
            teacher_id=payload.teacher_id,
            subject_ids=payload.subject_ids,
            max_students=payload.max_students,
        )

    def admin_assign_teacher(
        self,
        class_id: str,
        teacher_id: str,
    ) -> ClassSection | None:
        # Raises ClassNotFoundException inside SchoolService if not found
        return self.school_service.assign_teacher_to_class(
            class_id=class_id,
            teacher_id=teacher_id,
        )

    def admin_enroll_student(
        self,
        class_id: str,
        student_id: str,
    ) -> ClassSection | None:
        return self.school_service.enroll_student_to_class(
            class_id=class_id,
            student_id=student_id,
        )

    def admin_unenroll_student(
        self,
        class_id: str,
        student_id: str,
    ) -> ClassSection | None:
        return self.school_service.unenroll_student_from_class(
            class_id=class_id,
            student_id=student_id,
        )


    def admin_soft_delete_class(self, class_id: str, actor_id: str) -> bool:
        return self.school_service.soft_delete_class(class_id, actor_id)

    # ---------- Queries ----------

    def admin_get_class(self, class_id: str) -> Optional[dict]:
        """
        Read-only: returns raw Mongo dict or None.
        Route layer can:
        - map to AdminClassDataDTO
        - or let None become 404 via global handler
        """
        return self.class_read_model.get_by_id(class_id)

    def admin_list_classes_enriched(self) -> List[dict]:
        """
        Read-only: list all non-deleted classes.
        Later you can add pagination/filtering here.
        """
        return self.admin_read_model.admin_list_classes_enriched()

    def admin_list_classes_select(self) -> List[dict]:
        """
        Read-only: list all non-deleted classes.
        Later you can add pagination/filtering here.
        """
        return self.admin_read_model.admin_list_class_select()

    
    def admin_count_classes_for_teacher(self, teacher_id: str | ObjectId) -> int:
        return self.admin_read_model.admin_count_classes_for_teacher(teacher_id)



    def admin_list_students_in_class_select_options(self, class_id: str) -> List[dict]:
        return self.admin_read_model.admin_list_students_in_class_select_options(class_id)


    def admin_list_enrollment_student_select(self, class_id: str) -> List[dict]:
        return self.admin_read_model.admin_list_enrollment_student_select(class_id)