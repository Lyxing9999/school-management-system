from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.admin.data_transfer.requests import (
    AdminCreateStaffSchema, AdminUpdateStaffSchema
)
from app.contexts.admin.data_transfer.responses import AdminCreateStaffDataDTO
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO

@admin_bp.route("/staff", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_staff():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateStaffSchema)
    admin_id = get_current_user_id()
    user_dto, staff_dto = g.admin_facade.admin_create_staff(payload, admin_id)
    return AdminCreateStaffDataDTO(**{**user_dto.model_dump(), **staff_dto.model_dump()})


@admin_bp.route("/staff/<user_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_staff(user_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateStaffSchema)
    return g.admin_facade.admin_update_staff(user_id, payload)


@admin_bp.route("/staff/<staff_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_staff_by_id(staff_id: str):
    staff_dto: StaffBaseDataDTO = g.admin_facade.admin_get_staff_by_id(staff_id)
    return staff_dto


@admin_bp.route("/staff/name-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_staff_name_select():
    search_text = request.args.get("search", "")
    role = request.args.get("role", "teacher")
    return g.admin_facade.admin_get_staff_name_select(search_text, role)