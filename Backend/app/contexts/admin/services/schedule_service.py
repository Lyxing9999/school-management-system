from __future__ import annotations
from typing import Optional, List

from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.school_service import SchoolService
from app.contexts.school.domain.schedule import ScheduleSlot

from app.contexts.admin.data_transfer.request import (
    AdminCreateScheduleSlotSchema,
    AdminUpdateScheduleSlotSchema,
)
from app.contexts.admin.data_transfer.response import (AdminScheduleSlotDataDTO)

from app.contexts.shared.decorators.logging_decorator import log_operation
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel

from app.contexts.shared.model_converter import mongo_converter

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

    def admin_list_class_schedules(
        self,
        class_id: str | ObjectId,
    ) -> List[AdminScheduleSlotDataDTO]:
        return mongo_converter.list_to_dto(self.schedule_read_model.list_class_schedules(class_id=class_id), AdminScheduleSlotDataDTO)

    def admin_list_teacher_schedules(
        self,
        teacher_id: str | ObjectId,
    ) -> List[AdminScheduleSlotDataDTO]:
        return mongo_converter.list_to_dto(self.schedule_read_model.list_teacher_schedules(teacher_id=teacher_id), AdminScheduleSlotDataDTO)
