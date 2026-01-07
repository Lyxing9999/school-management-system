from typing import Dict, Any, Optional, List
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.legacy.school_service import SchoolService
from app.contexts.school.domain.schedule import ScheduleSlot

from app.contexts.admin.data_transfer.requests import (
    AdminCreateScheduleSlotSchema,
    AdminUpdateScheduleSlotSchema,
)

from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.admin.read_models.admin_read_model import AdminReadModel

from app.contexts.notifications.services.notification_service import NotificationService
from app.contexts.notifications.utils.recipient_resolver import NotificationRecipientResolver
from app.contexts.notifications.types import NotifType

from app.contexts.shared.model_converter import mongo_converter


class ScheduleAdminService:
    """
    Admin-facing application service for Schedule management.

    - Commands go through SchoolService (domain rules enforced).
    - Notifications emitted here (application layer).
    - Notification user_id must be IAM user_id (socket room id from JWT payload).
    """

    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        self.schedule_read_model = ScheduleReadModel(db)
        self.admin_read_model = AdminReadModel(db)

        self.notification_service = NotificationService(db)
        self.notif_resolver = NotificationRecipientResolver(db)

    # -----------------------------
    # Helpers
    # -----------------------------

    def oid(self, v: str | ObjectId | None) -> Optional[ObjectId]:
        if v is None:
            return None
        try:
            return mongo_converter.convert_to_object_id(v)
        except Exception:
            return None

    def _class_doc(self, class_id: str | ObjectId) -> dict:
        return self.admin_read_model.admin_get_class(class_id) or {}

    def _class_name(self, class_id: str | ObjectId) -> str:
        cls = self._class_doc(class_id)
        return (cls.get("name") or "Class").strip()

    def _class_student_ids(self, class_id: str | ObjectId) -> List[str]:
        """
        Adjust this mapping if your class doc uses another field name.
        Common patterns: student_ids, students, roster_student_ids...
        """
        cls = self._class_doc(class_id)
        raw = cls.get("student_ids") or cls.get("students") or []
        out: List[str] = []
        if isinstance(raw, list):
            for x in raw:
                if x:
                    out.append(str(x))
        return out

    def _notify_teacher(self, *, teacher_id: str | ObjectId | None, type_: str, title: str, message: str, data: dict):
        if not teacher_id:
            return
        teacher_user_id = self.notif_resolver.best_effort_user_id(teacher_id)
        if not teacher_user_id:
            return

        self.notification_service.create_for_user(
            user_id=str(teacher_user_id),
            role="teacher",
            type=type_,
            title=title,
            message=message,
            entity_type="schedule",
            entity_id=str(data.get("slot_id") or ""),
            data=data,
        )

    def _notify_students_in_class(self, *, class_id: str | ObjectId, type_: str, title: str, message: str, data: dict):
        student_ids = self._class_student_ids(class_id)
        if not student_ids:
            return

        for sid in student_ids:
            user_id = self.notif_resolver.student_to_user_id(sid)
            if not user_id:
                continue

            self.notification_service.create_for_user(
                user_id=str(user_id),
                role="student",
                type=type_,
                title=title,
                message=message,
                entity_type="schedule",
                entity_id=str(data.get("slot_id") or ""),
                data=data,
            )

    def _slot_payload(
        self,
        *,
        slot_id: str,
        class_id: str,
        class_name: str,
        teacher_id: Optional[str],
        day_of_week: Any,
        start_time: Any,
        end_time: Any,
        room: Optional[str],
        subject_id: Optional[str],
        route_teacher: str = "/teacher/schedule",
        route_student: str = "/student/schedule",
    ) -> dict:
        return {
            "route_teacher": route_teacher,
            "route_student": route_student,
            "slot_id": str(slot_id),
            "class_id": str(class_id),
            "class_name": class_name,
            "teacher_id": str(teacher_id) if teacher_id else None,
            "day_of_week": day_of_week,
            "start_time": start_time,
            "end_time": end_time,
            "room": room,
            "subject_id": str(subject_id) if subject_id else None,
        }

    # -----------------------------
    # Commands
    # -----------------------------

    def admin_create_schedule_slot(
        self,
        payload: AdminCreateScheduleSlotSchema,
        created_by: str | ObjectId,
    ) -> ScheduleSlot:
        slot = self.school_service.create_schedule_slot_for_class(
            class_id=payload.class_id,
            teacher_id=payload.teacher_id,
            day_of_week=payload.day_of_week,
            start_time=payload.start_time,
            end_time=payload.end_time,
            room=payload.room,
            subject_id=payload.subject_id if payload.subject_id else None,
        )

        class_id = str(payload.class_id)
        class_name = self._class_name(class_id)

        slot_id = str(getattr(slot, "id", None) or getattr(slot, "_id", None) or "")
        data = self._slot_payload(
            slot_id=slot_id,
            class_id=class_id,
            class_name=class_name,
            teacher_id=str(payload.teacher_id) if payload.teacher_id else None,
            day_of_week=payload.day_of_week,
            start_time=payload.start_time,
            end_time=payload.end_time,
            room=payload.room,
            subject_id=str(payload.subject_id) if payload.subject_id else None,
        )

        # Teacher: assigned
        self._notify_teacher(
            teacher_id=payload.teacher_id,
            type_=NotifType.SCHEDULE_ASSIGNED,
            title=f"New schedule assigned for {class_name}",
            message="A schedule slot has been created and assigned to you.",
            data=data,
        )

        # Students: updated
        self._notify_students_in_class(
            class_id=class_id,
            type_=NotifType.SCHEDULE_UPDATED,
            title=f"Schedule updated for {class_name}",
            message="Your class schedule has been updated.",
            data=data,
        )

        return slot

    def admin_update_schedule_slot(
        self,
        slot_id: str | ObjectId,
        payload: AdminUpdateScheduleSlotSchema,
        updated_by: str | ObjectId,
    ) -> ScheduleSlot:
        """
        Update slot (move day/time/room/subject). Notify teacher + students as UPDATED.
        """
        # Snapshot BEFORE update to know class_id / teacher_id if domain return doesn't include them
        before = self.schedule_read_model.get_by_id(slot_id)
        before_class_id = str((before or {}).get("class_id") or "")
        before_teacher_id = (before or {}).get("teacher_id")
        before_teacher_id_str = str(before_teacher_id) if before_teacher_id else None

        slot = self.school_service.move_schedule_slot(
            slot_id=slot_id,
            new_day_of_week=payload.day_of_week,
            new_start_time=payload.start_time,
            new_end_time=payload.end_time,
            new_room=payload.room if payload.room is not None else None,
            new_subject_id=payload.subject_id if payload.subject_id else None,
        )

        # Try read AFTER update for accurate data
        after = self.schedule_read_model.get_by_id(slot_id) or before or {}

        class_id = str(after.get("class_id") or before_class_id or "")
        class_name = self._class_name(class_id) if class_id else "Class"

        teacher_id = after.get("teacher_id") or before_teacher_id_str
        teacher_id_str = str(teacher_id) if teacher_id else None

        data = self._slot_payload(
            slot_id=str(slot_id),
            class_id=class_id,
            class_name=class_name,
            teacher_id=teacher_id_str,
            day_of_week=after.get("day_of_week") or payload.day_of_week,
            start_time=after.get("start_time") or payload.start_time,
            end_time=after.get("end_time") or payload.end_time,
            room=after.get("room"),
            subject_id=str(after.get("subject_id")) if after.get("subject_id") else None,
        )

        # Teacher: updated
        self._notify_teacher(
            teacher_id=teacher_id_str,
            type_=NotifType.SCHEDULE_UPDATED,
            title=f"Schedule updated for {class_name}",
            message="A schedule slot you are involved in has been updated.",
            data=data,
        )

        # Students: updated
        if class_id:
            self._notify_students_in_class(
                class_id=class_id,
                type_=NotifType.SCHEDULE_UPDATED,
                title=f"Schedule updated for {class_name}",
                message="Your class schedule has been updated.",
                data=data,
            )

        return slot

    def admin_delete_schedule_slot(
        self,
        slot_id: str | ObjectId,
        deleted_by: str | ObjectId,
    ) -> None:
        """
        Optional but recommended: notify teacher + students schedule updated after delete.
        """
        before = self.schedule_read_model.get_by_id(slot_id) or {}
        class_id = str(before.get("class_id") or "")
        class_name = self._class_name(class_id) if class_id else "Class"
        teacher_id = before.get("teacher_id")
        teacher_id_str = str(teacher_id) if teacher_id else None

        self.school_service.soft_delete_schedule_slot(slot_id=slot_id, actor_id=deleted_by)

        data = self._slot_payload(
            slot_id=str(slot_id),
            class_id=class_id,
            class_name=class_name,
            teacher_id=teacher_id_str,
            day_of_week=before.get("day_of_week"),
            start_time=before.get("start_time"),
            end_time=before.get("end_time"),
            room=before.get("room"),
            subject_id=str(before.get("subject_id")) if before.get("subject_id") else None,
        )

        self._notify_teacher(
            teacher_id=teacher_id_str,
            type_=NotifType.SCHEDULE_UPDATED,
            title=f"Schedule updated for {class_name}",
            message="A schedule slot has been removed/disabled.",
            data=data,
        )

        if class_id:
            self._notify_students_in_class(
                class_id=class_id,
                type_=NotifType.SCHEDULE_UPDATED,
                title=f"Schedule updated for {class_name}",
                message="Your class schedule has been updated.",
                data=data,
            )

    # -----------------------------
    # Queries (unchanged)
    # -----------------------------

    def admin_list_schedules_for_class_enriched(
        self,
        class_id: str | ObjectId,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        return self.admin_read_model.admin_list_schedules_for_class_enriched(
            class_id=class_id,
            page=page,
            page_size=page_size,
        )

    def admin_list_schedules_for_teacher_enriched(
        self,
        teacher_id: str | ObjectId,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        return self.admin_read_model.admin_list_schedules_for_teacher_enriched(
            teacher_id=teacher_id,
            page=page,
            page_size=page_size,
        )

    def admin_get_schedule_by_id(self, slot_id: str | ObjectId) -> dict:
        return self.admin_read_model.admin_get_schedule_by_id(slot_id=slot_id)

    def admin_count_schedules_for_teacher(self, teacher_id: str | ObjectId) -> int:
        return self.admin_read_model.admin_count_schedules_for_teacher(teacher_id)