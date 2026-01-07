from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter
from app.contexts.admin.data_transfer.requests import (
    AdminCreateSubjectSchema,
    AdminUpdateSubjectSchema,
)

# Response DTOs - adjust to your actual names/paths
from app.contexts.admin.data_transfer.responses import (
    AdminSubjectPaginatedDTO,     
    AdminSubjectDataDTO,          
    AdminSubjectNameSelectDTO,   
    AdminSubjectNameSelectListDTO 
      
)

from app.contexts.admin.mapper.school_admin_mapper import SchoolAdminMapper



@admin_bp.route("/subjects/<subject_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_subject(subject_id: str):
    subject = g.admin.subject_service.admin_get_subject(subject_id)
    return SchoolAdminMapper.subject_to_dto(subject)
    

@admin_bp.route("/subjects", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_subjects_paginated():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 5))
    status = request.args.get("status", "all")
    search = request.args.get("search")

    cursor, total = g.admin.subject_service.admin_list_subjects(
        status=status,
        page=page,
        page_size=page_size,
        search=search,
    )
    items = mongo_converter.list_to_dto(cursor, AdminSubjectDataDTO)

    page_size_safe = max(page_size, 1)

    return AdminSubjectPaginatedDTO(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max((total + page_size_safe - 1) // page_size_safe, 1),
    )


@admin_bp.route("/subjects", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_create_subject():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateSubjectSchema)
    admin_id = get_current_staff_id()

    subject = g.admin.subject_service.admin_create_subject(
        payload=payload, 
        created_by=admin_id
    )
    return SchoolAdminMapper.subject_to_dto(subject)


@admin_bp.route("/subjects/<subject_id>/deactivate", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_deactivate_subject(subject_id: str):
    subject = g.admin.subject_service.admin_deactivate_subject(subject_id)
    return SchoolAdminMapper.subject_to_dto(subject)


@admin_bp.route("/subjects/<subject_id>/activate", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_activate_subject(subject_id: str):
    subject = g.admin.subject_service.admin_activate_subject(subject_id)
    return SchoolAdminMapper.subject_to_dto(subject)

@admin_bp.route("/subjects/<subject_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_patch_subject(subject_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateSubjectSchema)
    patch_data = payload.model_dump(exclude_unset=True)
    subject = g.admin.subject_service.admin_update_subject_patch(subject_id, patch_data)
    return SchoolAdminMapper.subject_to_dto(subject)

@admin_bp.route("/subjects/<subject_id>/soft-delete", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_soft_delete_subject(subject_id: str):
    admin_id = get_current_staff_id()
    ok = g.admin.subject_service.admin_soft_delete_subject(subject_id, admin_id)
    return {"ok": ok}

@admin_bp.route("/subjects/names-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_subject_name_select():
    subject_list = g.admin.subject_service.admin_list_subject_name_select()
    subject_dto = mongo_converter.list_to_dto(subject_list, AdminSubjectNameSelectDTO)
    return AdminSubjectNameSelectListDTO(items=subject_dto)
