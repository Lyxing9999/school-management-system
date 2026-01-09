from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter

from app.contexts.admin.data_transfer.requests import (
    AdminCreateScheduleSlotSchema,
    AdminUpdateScheduleSlotSchema,
    AdminAssignScheduleSlotSubjectSchema
)
from app.contexts.admin.data_transfer.responses import (
    AdminScheduleSlotDataDTO,
    AdminScheduleListDTO,
)
from app.contexts.admin.mapper.school_admin_mapper import SchoolAdminMapper



#helper function
def _get_pagination():
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)

    page = max(1, page)
    page_size = min(max(1, page_size), 100)  # clamp
    return page, page_size

# ---------------------------------------------------------
# CREATE schedule slot
# ---------------------------------------------------------
@admin_bp.route("/schedule/slots", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_create_schedule_slot():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateScheduleSlotSchema)
    admin_id = get_current_staff_id()
    slot = g.admin.schedule_service.admin_create_schedule_slot(payload=payload, created_by=admin_id)
    dto: AdminScheduleSlotDataDTO = SchoolAdminMapper.schedule_slot_to_dto(slot)
    return dto



# ---------------------------------------------------------
# UPDATE schedule slot
# ---------------------------------------------------------
@admin_bp.route("/schedule/slots/<slot_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_schedule_slot(slot_id: str):
    payload = pydantic_converter.convert_to_model(request.json,AdminUpdateScheduleSlotSchema,)
    admin_id = get_current_staff_id()
    slot = g.admin.schedule_service.admin_update_schedule_slot(slot_id=slot_id, payload=payload, updated_by=admin_id)
    dto: AdminScheduleSlotDataDTO = SchoolAdminMapper.schedule_slot_to_dto(slot)
    return dto


@admin_bp.route("/schedule/slots/<slot_id>/subject", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_assign_subject_to_schedule_slot(slot_id: str):
    payload = pydantic_converter.convert_to_model(
        request.json,
        AdminAssignScheduleSlotSubjectSchema,
    )

    admin_id = get_current_staff_id()

    slot = g.admin.schedule_service.admin_assign_subject_to_schedule_slot(
        slot_id=slot_id,
        subject_id=payload.subject_id,   

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
    admin_id = get_current_staff_id()
    g.admin.schedule_service.admin_delete_schedule_slot(slot_id=slot_id, deleted_by=admin_id)
    return {"message": "Schedule slot deleted successfully"}


# ---------------------------------------------------------
# LIST schedule for a CLASS
# ---------------------------------------------------------
@admin_bp.route("/schedule/classes/<class_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_schedules_for_class_enriched(class_id: str):
    page, page_size = _get_pagination()
    result = g.admin.schedule_service.admin_list_schedules_for_class_enriched(
        class_id=class_id,
        page=page,
        page_size=page_size,
    )
    items_dto = mongo_converter.list_to_dto(result.get("items", []), AdminScheduleSlotDataDTO)
    return AdminScheduleListDTO(
        items=items_dto,
        total=result.get("total", 0),
        page=result.get("page", page),
        page_size=result.get("page_size", page_size),
    )

# ---------------------------------------------------------
# LIST schedule for a TEACHER
# ---------------------------------------------------------
@admin_bp.route("/schedule/teachers/<teacher_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_schedules_for_teacher_enriched(teacher_id: str):
    page, page_size = _get_pagination()
    result = g.admin.schedule_service.admin_list_schedules_for_teacher_enriched(
        teacher_id=teacher_id,
        page=page,
        page_size=page_size,
    )
    items_dto = mongo_converter.list_to_dto(result.get("items", []), AdminScheduleSlotDataDTO)
    return AdminScheduleListDTO(
        items=items_dto,
        total=result.get("total", 0),
        page=result.get("page", page),
        page_size=result.get("page_size", page_size),
    )


    
@admin_bp.route("/schedule/slots/<slot_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_schedule_by_id(slot_id: str):
    slot = g.admin.schedule_service.admin_get_schedule_by_id(slot_id=slot_id)
    return mongo_converter.doc_to_dto(slot, AdminScheduleSlotDataDTO)


@admin_bp.route("/schedule/teacher-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_schedule_teacher_select():
    class_id = request.args.get("class_id", type=str)
    subject_id = request.args.get("subject_id", type=str)
    if not class_id or not subject_id:
        return {"items": []}

    items = g.admin.schedule_service.admin_list_teacher_select_for_class_subject(class_id, subject_id)
    return {"items": items}