from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.admin.data_transfer.requests import (
    AdminCreateStaffSchema, AdminUpdateStaffSchema
)
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.staff.mapper.staff_mapper import StaffMapper
from app.contexts.admin.data_transfer.responses import AdminUserStaffDataDTO, AdminTeacherSelectListDTO, AdminTeacherSelectDTO


@admin_bp.route("/staff", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_staff():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateStaffSchema)
    admin_id = get_current_staff_id()

    user_dto, staff_dto = g.admin.facade.admin_create_staff_workflow(payload, admin_id)
    user_dto = IAMMapper.to_dto(user_dto)
    staff_dto = StaffMapper.to_dto(staff_dto)
    return AdminUserStaffDataDTO(**{**user_dto.model_dump(), **staff_dto.model_dump()})


@admin_bp.route("/staff/<user_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_staff(user_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateStaffSchema)
    staff = g.admin.staff_service.admin_update_staff(user_id, payload)
    return StaffMapper.to_dto(staff)



@admin_bp.route("/staff/<user_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_staff_by_id(user_id: str):
    staff = g.admin.staff_service.admin_get_staff_by_user_id(user_id)
    return StaffMapper.to_dto(staff)



@admin_bp.route("/staff/teacher-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_teacher_select():
    teacher_list = g.admin.staff_service.admin_list_teacher_select()
    teacher_dto = mongo_converter.list_to_dto(teacher_list, AdminTeacherSelectDTO)
    return AdminTeacherSelectListDTO(items=teacher_dto)


