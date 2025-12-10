from __future__ import annotations
from typing import  List

from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.domain.schedule import ScheduleSlot

from app.contexts.admin.data_transfer.request import (
    AdminCreateScheduleSlotSchema,
    AdminUpdateScheduleSlotSchema,
)
from app.contexts.shared.decorators.logging_decorator import log_operation
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
class ScheduleAdminService:
    """
    Admin-facing application service for Schedule management.

    Thin façade over SchoolService.
    Domain errors are raised by SchoolService and handled by
    your global error handler → HTTP errors.
    """

    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        self.schedule_read_model = ScheduleReadModel(db)
        self.admin_read_model = AdminReadModel(db)
    
    # ---------- Commands ----------

    @log_operation(level="INFO")
    def admin_create_schedule_slot(
        self,
        payload: AdminCreateScheduleSlotSchema,
        created_by: str | ObjectId,
    ) -> ScheduleSlot:
        return self.school_service.create_schedule_slot_for_class(
            class_id=payload.class_id,
            teacher_id=payload.teacher_id,
            day_of_week=payload.day_of_week,
            start_time=payload.start_time,
            end_time=payload.end_time,
            room=payload.room,
        )

    @log_operation(level="INFO")
    def admin_update_schedule_slot(
        self,
        slot_id: str | ObjectId,
        payload: AdminUpdateScheduleSlotSchema,
        updated_by: str | ObjectId,
    ) -> ScheduleSlot:
        return self.school_service.move_schedule_slot(
            slot_id=slot_id,
            new_day_of_week=payload.day_of_week,
            new_start_time=payload.start_time,
            new_end_time=payload.end_time,
            new_room=payload.room,
        )

    @log_operation(level="INFO")
    def admin_delete_schedule_slot(
        self,
        slot_id: str | ObjectId,
        deleted_by: str | ObjectId,
    ) -> None:
        self.school_service.delete_schedule_slot(slot_id)

    # ---------- Queries ----------
    def admin_list_schedules_for_class_enriched(
        self,
        class_id: str | ObjectId,
    ) -> List[dict]:
        schedules = self.admin_read_model.admin_list_schedules_for_class_enriched(class_id=class_id)
        return schedules
        
    def admin_list_schedules_for_teacher_enriched(
        self,
        teacher_id: str | ObjectId,
    ) -> List[dict]:
        return self.admin_read_model.admin_list_schedules_for_teacher_enriched(teacher_id=teacher_id)


    def admin_get_schedule_by_id(
        self,
        slot_id: str | ObjectId,
    ) -> dict:
        return self.admin_read_model.admin_get_schedule_by_id(slot_id=slot_id)

    def admin_count_schedules_for_teacher(
        self,
        teacher_id: str | ObjectId,
    ) -> int:
        return self.admin_read_model.admin_count_schedules_for_teacher(teacher_id)