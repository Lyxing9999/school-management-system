from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.admin.data_transfer.request import (
    AdminCreateStaffSchema, AdminUpdateStaffSchema
)
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.staff.domain import StaffMapper
from app.contexts.admin.data_transfer.response import AdminCreateStaffDataDTO, AdminTeacherListDTO, AdminTeacherSelectDTO


@admin_bp.route("/staff", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_staff():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateStaffSchema)
    admin_id = get_current_user_id()

    user_dto, staff_dto = g.admin.facade.admin_create_staff_workflow(payload, admin_id)
    user_dto = IAMMapper.to_dto(user_dto)
    staff_dto = StaffMapper.to_dto(staff_dto)
    return AdminCreateStaffDataDTO(**{**user_dto.model_dump(), **staff_dto.model_dump()})


@admin_bp.route("/staff/<user_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_staff(user_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateStaffSchema)
    staff = g.admin.staff_service.admin_update_staff(user_id, payload)
    return StaffMapper.to_dto(staff)



@admin_bp.route("/staff/<staff_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_staff_by_id(staff_id: str):
    staff = g.admin.staff_service.admin_get_staff_by_id(staff_id)
    return StaffMapper.to_dto(staff)



@admin_bp.route("/staff/teacher-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_teacher_select():
    teacher_list = g.admin.staff_service.admin_get_teacher_select()
    print(teacher_list)
    teacher_dto = mongo_converter.list_to_dto(teacher_list, AdminTeacherSelectDTO)
    return AdminTeacherListDTO(items=teacher_dto)


