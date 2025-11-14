from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.auth.jwt_utils import role_required
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.admin.data_transfer.requests import AdminCreateClassSchema, AdminUpdateClassSchema

@admin_bp.route("/classes", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_class():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateClassSchema)
    admin_id = get_current_user_id()
    return g.admin_facade.admin_create_class(payload, created_by=admin_id)

@admin_bp.route("/classes", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_classes():
    return g.admin_facade.class_service.admin_get_classes()

@admin_bp.route("/classes/<class_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_class(class_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateClassSchema)
    return g.admin_facade.class_service.admin_update_class(class_id, payload)

@admin_bp.route("/classes/<class_id>/teacher", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def assign_teacher(class_id: str):
    teacher_id = request.json.get("teacher_id")
    return g.admin_facade.class_service.admin_assign_teacher(class_id, teacher_id)

@admin_bp.route("/classes/<class_id>/students", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def assign_student(class_id: str):
    student_id = request.json.get("student_id")
    return g.admin_facade.class_service.admin_assign_student(class_id, student_id)