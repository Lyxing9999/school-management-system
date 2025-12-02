from __future__ import annotations
from flask import request, g

from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter

from app.contexts.admin.data_transfer.request import (
    AdminCreateClassSchema,
    AdminAssignTeacherToClassSchema,
    AdminEnrollStudentToClassSchema,
    AdminUnAssignTeacherToClassSchema
)
from app.contexts.admin.mapper.school_admin_mapper import SchoolAdminMapper
from app.contexts.admin.data_transfer.response import AdminClassSelectListDTO, AdminClassSelectDTO, AdminClassDataDTO, AdminClassListDTO   


@admin_bp.route("/classes", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_create_class():
    payload = pydantic_converter.convert_to_model(
        request.json,
        AdminCreateClassSchema,
    )
    admin_id = get_current_user_id()

    section = g.admin.class_service.admin_create_class(
        payload=payload,
        created_by=admin_id,
    )
    return SchoolAdminMapper.class_to_dto(section)


@admin_bp.route("/classes", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_classes():
    classes = g.admin.class_service.admin_list_classes_enriched()
    items = mongo_converter.list_to_dto(classes, AdminClassDataDTO)
    return AdminClassListDTO(items=items)


@admin_bp.route("/classes/<class_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_class(class_id: str):
    class_doc = g.admin.class_service.admin_get_class(class_id)
    return SchoolAdminMapper.class_doc_to_dto(class_doc)


@admin_bp.route("/classes/<class_id>/teacher", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_assign_teacher_to_class(class_id: str):
    payload = pydantic_converter.convert_to_model(
        request.json,
        AdminAssignTeacherToClassSchema,
    )
    section = g.admin.class_service.admin_assign_teacher(
        class_id=class_id,
        teacher_id=payload.teacher_id,
    )
    return SchoolAdminMapper.class_to_dto(section)


@admin_bp.route("/classes/<class_id>/teacher", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_unassign_teacher_to_class(class_id: str):
    section = g.admin.class_service.admin_unassign_teacher(class_id=class_id)
    return SchoolAdminMapper.class_to_dto(section)

@admin_bp.route("/classes/<class_id>/students", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_enroll_student_to_class(class_id: str):
    payload = pydantic_converter.convert_to_model(
        request.json,
        AdminEnrollStudentToClassSchema,
    )
    section = g.admin.class_service.admin_enroll_student(
        class_id=class_id,
        student_id=payload.student_id,
    )
    
    return SchoolAdminMapper.class_to_dto(section)


@admin_bp.route("/classes/<class_id>/students/<student_id>", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_unenroll_student_from_class(class_id: str, student_id: str):
    section = g.admin.class_service.admin_unenroll_student(
        class_id=class_id,
        student_id=student_id,
    )
    return SchoolAdminMapper.class_to_dto(section)


@admin_bp.route("/classes/<class_id>/soft-delete", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_soft_delete_class(class_id: str):
    g.admin.class_service.admin_soft_delete_class(class_id)
    return {"message": "Class soft deleted"}



# ---------------------------------------------------------
# LIST Classes Select
# ---------------------------------------------------------
@admin_bp.route("/classes/names-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_classes_select():
    classes = g.admin.class_service.admin_list_classes_select()
    items = mongo_converter.list_to_dto(classes, AdminClassSelectDTO)
    return AdminClassSelectListDTO(items=items)


