from typing import Optional, List, Union, Dict, Any

from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.legacy.school_service import SchoolService
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.admin.read_models.admin_read_model import AdminReadModel

from app.contexts.notifications.services.notification_service import NotificationService
from app.contexts.notifications.utils.recipient_resolver import NotificationRecipientResolver
from app.contexts.notifications.types import NotifType

from app.contexts.school.domain.class_section import ClassSection, ClassSectionStatus 
from app.contexts.admin.data_transfer.requests import AdminCreateClassSchema, AdminUpdateClassRelationsSchema

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.school.domain.value_objects.class_roster_update import ClassRosterUpdate


class ClassAdminService:
    """
    Admin-facing application service for Class/Section management.

    Principles:
    - Commands go through SchoolService (domain rules enforced).
    - Notifications are emitted here (application layer), NOT in read models.
    - Notification user_id must be IAM user_id (Socket room id from JWT payload).
    """

    def __init__(self, db: Database):
        self.db = db
        self.school_service = SchoolService(db)

        self.class_read_model = ClassReadModel(db)
        self.admin_read_model = AdminReadModel(db)

        self.notification_service = NotificationService(db)
        self.notif_resolver = NotificationRecipientResolver(db)

    # -----------------------------
    # Helpers
    # -----------------------------

    def oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def _class_name(self, class_id: str) -> str:
        cls = self.admin_read_model.admin_get_class(class_id) or {}
        return (cls.get("name") or "Class").strip()

    # -----------------------------
    # Teacher notifications (BACKWARD COMPAT)
    # -----------------------------

    def _notify_teacher_assigned(
        self,
        *,
        class_id: str,
        class_name: str,
        homeroom_teacher_id: Optional[str] = None,
        teacher_id: Optional[str] = None,  # backward compatible alias
    ) -> None:
        """
        Accepts either homeroom_teacher_id or teacher_id.
        Resolver best_effort_user_id can handle staff_id or IAM user_id.
        """
        tid = (homeroom_teacher_id or teacher_id or "").strip()
        if not tid:
            return

        teacher_user_id = self.notif_resolver.best_effort_user_id(tid)
        if not teacher_user_id:
            return

        self.notification_service.create_for_user(
            user_id=teacher_user_id,
            role="teacher",
            type=NotifType.CLASS_ASSIGNMENT,
            title=f"You are assigned to {class_name}",
            message="Your class assignment has been updated.",
            entity_type="class",
            entity_id=str(class_id),
            data={
                "route": f"/teacher/classes/{class_id}",
                "class_id": str(class_id),
                "class_name": class_name,
            },
        )

    def _notify_teacher_unassigned(
        self,
        *,
        class_id: str,
        class_name: str,
        homeroom_teacher_id: Optional[str] = None,
        teacher_id: Optional[str] = None,  # backward compatible alias
    ) -> None:
        tid = (homeroom_teacher_id or teacher_id or "").strip()
        if not tid:
            return

        teacher_user_id = self.notif_resolver.best_effort_user_id(tid)
        if not teacher_user_id:
            return

        self.notification_service.create_for_user(
            user_id=teacher_user_id,
            role="teacher",
            type=NotifType.CLASS_UNASSIGNED,
            title=f"You are unassigned from {class_name}",
            message="You no longer have access to this class as a teacher.",
            entity_type="class",
            entity_id=str(class_id),
            data={
                "route": "/teacher/classes",
                "class_id": str(class_id),
                "class_name": class_name,
            },
        )

    def _notify_student_enrolled(self, *, student_id: str, class_id: str, class_name: str) -> None:
        student_user_id = self.notif_resolver.student_to_user_id(student_id)
        if not student_user_id:
            return

        self.notification_service.create_for_user(
            user_id=student_user_id,
            role="student",
            type=NotifType.CLASS_ENROLLED,
            title=f"You were enrolled in {class_name}",
            message="You have been added to a class.",
            entity_type="class",
            entity_id=str(class_id),
            data={
                "route": f"/student/classes/{class_id}",
                "class_id": str(class_id),
                "class_name": class_name,
            },
        )

    def _notify_student_removed(self, *, student_id: str, class_id: str, class_name: str) -> None:
        student_user_id = self.notif_resolver.student_to_user_id(student_id)
        if not student_user_id:
            return

        self.notification_service.create_for_user(
            user_id=student_user_id,
            role="student",
            type=NotifType.CLASS_REMOVED,
            title=f"You were removed from {class_name}",
            message="You have been removed from a class.",
            entity_type="class",
            entity_id=str(class_id),
            data={
                "route": "/student/classes",
                "class_id": str(class_id),
                "class_name": class_name,
            },
        )

    # -----------------------------
    # Commands
    # -----------------------------

    def admin_create_class(
        self,
        payload: AdminCreateClassSchema,
        created_by: str | ObjectId,
    ) -> ClassSection:
        """
        Creates class and notifies teacher (if homeroom_teacher_id provided).
        """
        cls = self.school_service.create_class(
            name=payload.name,
            homeroom_teacher_id=payload.homeroom_teacher_id,
            subject_ids=payload.subject_ids,
            max_students=payload.max_students,
        )

        class_id = str(cls.id) if hasattr(cls, "id") else str(getattr(cls, "_id", ""))
        class_name = (payload.name or "Class").strip()

        if getattr(payload, "homeroom_teacher_id", None):
            self._notify_teacher_assigned(
                homeroom_teacher_id=str(payload.homeroom_teacher_id),
                class_id=class_id,
                class_name=class_name,
            )

        return cls

    def admin_assign_teacher(self, class_id: str, homeroom_teacher_id: str) -> ClassSection | None:
        before = self.admin_read_model.admin_get_class(class_id) or {}
        class_name = (before.get("name") or "Class").strip()

        old_teacher_raw = before.get("homeroom_teacher_id")
        old_teacher_id = str(old_teacher_raw) if old_teacher_raw else None

        cls = self.school_service.assign_teacher_to_class(
            class_id=class_id,
            homeroom_teacher_id=homeroom_teacher_id,
        )
        if not cls:
            return None

        new_teacher_id = str(homeroom_teacher_id)

        if old_teacher_id and old_teacher_id != new_teacher_id:
            self._notify_teacher_unassigned(
                homeroom_teacher_id=old_teacher_id,
                class_id=str(class_id),
                class_name=class_name,
            )

        self._notify_teacher_assigned(
            homeroom_teacher_id=new_teacher_id,
            class_id=str(class_id),
            class_name=class_name,
        )

        return cls

    def admin_set_class_status(self, class_id: str, status: ClassSectionStatus) -> Optional[dict]:
        return self.school_service.set_class_status(class_id, status)

    def admin_enroll_student(self, class_id: str, student_id: str) -> ClassSection | None:
        cls = self.school_service.enroll_student_to_class(
            class_id=class_id,
            student_id=student_id,
        )
        if not cls:
            return None

        class_name = self._class_name(class_id)
        self._notify_student_enrolled(
            student_id=str(student_id),
            class_id=str(class_id),
            class_name=class_name,
        )
        return cls

    def admin_unenroll_student(self, class_id: str, student_id: str) -> ClassSection | None:
        cls = self.school_service.unenroll_student_from_class(
            class_id=class_id,
            student_id=student_id,
        )
        if not cls:
            return None

        class_name = self._class_name(class_id)
        self._notify_student_removed(
            student_id=str(student_id),
            class_id=str(class_id),
            class_name=class_name,
        )
        return cls

    def admin_soft_delete_class(self, class_id: str, actor_id: str) -> bool:
        return self.school_service.soft_delete_class(class_id, actor_id)

    def admin_update_class_relations(
        self,
        payload: AdminUpdateClassRelationsSchema,
        *,
        class_id: str,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        # 1) Snapshot BEFORE update
        before = self.admin_read_model.admin_get_class(class_id) or {}
        class_name = (before.get("name") or "Class").strip()

        old_teacher_raw = before.get("homeroom_teacher_id")
        old_teacher_id = str(old_teacher_raw) if old_teacher_raw else None

        # 2) Build VO
        class_oid = self.oid(class_id)
        student_oids = [self.oid(sid) for sid in (payload.student_ids or [])]
        homeroom_teacher_oid = self.oid(payload.homeroom_teacher_id) if payload.homeroom_teacher_id else None

        update_vo = ClassRosterUpdate.from_payload(
            class_id=class_oid,
            student_ids=student_oids,
            homeroom_teacher_id=homeroom_teacher_oid,
        )

        # 3) Apply domain update
        result = self.school_service.update_class_relations(update_vo)

        # 4) Read result
        added_ids = [str(x) for x in (result.get("added") or [])]
        removed_ids = [str(x) for x in (result.get("removed") or [])]

        new_teacher_raw = result.get("homeroom_teacher_id")
        new_teacher_id = str(new_teacher_raw) if new_teacher_raw else None

        # 5) Teacher notifications (state-based)
        old_tid = (old_teacher_id or "").strip()
        new_tid = (new_teacher_id or "").strip()

        if old_tid and old_tid != new_tid:
            self._notify_teacher_unassigned(
                homeroom_teacher_id=old_tid, 
                class_id=str(class_id),
                class_name=class_name,
            )

        if new_tid and old_tid != new_tid:
            self._notify_teacher_assigned(
                homeroom_teacher_id=new_tid,  
                class_id=str(class_id),
                class_name=class_name,
            )

        # 6) Student notifications
        for sid in added_ids:
            self._notify_student_enrolled(
                student_id=sid,
                class_id=str(class_id),
                class_name=class_name,
            )

        for sid in removed_ids:
            self._notify_student_removed(
                student_id=sid,
                class_id=str(class_id),
                class_name=class_name,
            )

        return {
            "class_id": result.get("class_id"),
            "homeroom_teacher_changed": result.get("homeroom_teacher_changed"),
            "homeroom_teacher_id": result.get("homeroom_teacher_id"),
            "enrolled_count": result.get("enrolled_count"),
            "added": result.get("added"),
            "removed": result.get("removed"),
            "conflicts": result.get("conflicts"),
            "capacity_rejected": result.get("capacity_rejected"),
        }

    # -----------------------------
    # Queries
    # -----------------------------

    def admin_get_class(self, class_id: str) -> Optional[dict]:
        return self.admin_read_model.admin_get_class(class_id)

    def admin_list_classes_enriched(
        self,
        *,
        q: str = "",
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
        deleted_only: bool = False,
        status: str | None = None,
    ) -> dict:
        items, total = self.admin_read_model.admin_list_classes_enriched(
            q=q,
            page=page,
            page_size=page_size,
            include_deleted=include_deleted,
            deleted_only=deleted_only,
            status=status,
        )
        return {"items": items, "total": total}

    def admin_list_classes_select(self) -> List[dict]:
        return self.admin_read_model.admin_list_class_select()

    def admin_count_classes_for_teacher(self, homeroom_teacher_id: str | ObjectId) -> int:
        return self.admin_read_model.admin_count_classes_for_teacher(homeroom_teacher_id)

    def admin_list_students_in_class_select(self, class_id: str) -> List[dict]:
        return self.admin_read_model.admin_list_students_in_class_select(class_id)

    def admin_search_enrollment_student_select(
        self,
        class_id: str,
        *,
        q: str = "",
        limit: int = 20,
    ) -> List[dict]:
        return self.admin_read_model.admin_search_enrollment_student_select(
            class_id, q=q, limit=limit
        )

    def admin_list_subjects_select_in_class(self, class_id: str) -> List[dict]:
        return self.admin_read_model.admin_list_subjects_select_in_class(class_id)



    