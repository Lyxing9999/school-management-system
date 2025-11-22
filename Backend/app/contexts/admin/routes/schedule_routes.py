from __future__ import annotations
from flask import request, g

from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter

from app.contexts.admin.data_transfer.request import (
    AdminCreateScheduleSlotSchema,
    AdminUpdateScheduleSlotSchema,
)
from app.contexts.admin.data_transfer.response import (
    AdminScheduleSlotDataDTO,
)
from app.contexts.admin.mapper.school_admin_mapper import SchoolAdminMapper


# ---------------------------------------------------------
# CREATE schedule slot
# ---------------------------------------------------------
@admin_bp.route("/schedule/slots", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_create_schedule_slot():
    """
    Create a new schedule slot for a class.
    Body → AdminCreateScheduleSlotSchema
    """
    payload = pydantic_converter.convert_to_model(
        request.json,
        AdminCreateScheduleSlotSchema,
    )
    admin_id = get_current_user_id()

    slot = g.admin_facade.schedule_service.admin_create_schedule_slot(
        payload=payload,
        created_by=admin_id,
    )

    dto: AdminScheduleSlotDataDTO = SchoolAdminMapper.schedule_slot_to_dto(slot)
    return dto


# ---------------------------------------------------------
# UPDATE schedule slot
# ---------------------------------------------------------
@admin_bp.route("/schedule/slots/<slot_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_schedule_slot(slot_id: str):
    """
    Update / move existing schedule slot.
    Body → AdminUpdateScheduleSlotSchema
    """
    payload = pydantic_converter.convert_to_model(
        request.json,
        AdminUpdateScheduleSlotSchema,
    )
    admin_id = get_current_user_id()

    slot = g.admin_facade.schedule_service.admin_update_schedule_slot(
        slot_id=slot_id,
        payload=payload,
        updated_by=admin_id,
    )

    dto: AdminScheduleSlotDataDTO = SchoolAdminMapper.schedule_slot_to_dto(slot)
    return dto


# ---------------------------------------------------------
# DELETE schedule slot
# ---------------------------------------------------------
@admin_bp.route("/schedule/slots/<slot_id>", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_delete_schedule_slot(slot_id: str):
    """
    Delete a schedule slot.
    (Your SchoolService currently does hard delete; you can change to soft later.)
    """
    admin_id = get_current_user_id()

    g.admin_facade.schedule_service.admin_delete_schedule_slot(
        slot_id=slot_id,
        deleted_by=admin_id,
    )
    return {"message": "Schedule slot deleted successfully"}


# ---------------------------------------------------------
# LIST schedule for a CLASS
# ---------------------------------------------------------
@admin_bp.route("/schedule/classes/<class_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_schedule_for_class(class_id: str):
    """
    List all schedule slots for a given class.
    """
    slots = g.admin_facade.schedule_service.admin_list_schedule_for_class(
        class_id=class_id,
    )
    return SchoolAdminMapper.schedule_list_to_dto(slots)


# ---------------------------------------------------------
# LIST schedule for a TEACHER
# ---------------------------------------------------------
@admin_bp.route("/schedule/teachers/<teacher_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_schedule_for_teacher(teacher_id: str):
    """
    List all schedule slots for a given teacher.
    Useful for admin overview / conflict debugging.
    """
    slots = g.admin_facade.schedule_service.admin_list_schedule_for_teacher(
        teacher_id=teacher_id,
    )
    return SchoolAdminMapper.schedule_list_to_dto(slots)