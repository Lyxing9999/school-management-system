from __future__ import annotations
from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.admin.data_transfer.request import AdminCreateUserSchema, AdminUpdateUserSchema
from app.contexts.admin.data_transfer.response import (
    PaginatedUsersDataDTO,
    AdminStudentNameSelectDTO,
    AdminStudentNameSelectListDTO,
    AdminUserStaffDataDTO   
)
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.iam.mapper.iam_mapper import IAMMapper 
from app.contexts.admin.data_transfer.response import PaginatedUserItemDTO
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from app.contexts.shared.model_converter import mongo_converter

@admin_bp.route("/users", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_users_paginated():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 5))
    roles = request.args.getlist("role[]") or request.args.getlist("role")
    cursor, total = g.admin.user_service.admin_get_users(
        roles, page=page, page_size=page_size
    )
    cursor = mongo_converter.list_to_dto(cursor, PaginatedUserItemDTO)
    return PaginatedUsersDataDTO(
        users=cursor,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max((total + page_size - 1) // page_size, 1)
    )


@admin_bp.route('/users', methods=['POST'])
@role_required(["admin"])
@wrap_response
def admin_create_user():
    user_schema = pydantic_converter.convert_to_model(request.json, AdminCreateUserSchema)
    admin_id = get_current_user_id()
    user_response_dto = g.admin.user_service.admin_create_user(
        user_schema, created_by=admin_id
    )
    return IAMMapper.to_dto(user_response_dto)

@admin_bp.route('/users/<user_id>', methods=['PATCH'])
@role_required(["admin"])
@wrap_response
def admin_update_user(user_id):
    user_schema = pydantic_converter.convert_to_model(request.json, AdminUpdateUserSchema)
    user_update_dto = g.admin.user_service.admin_update_user(user_id, user_schema)
    return IAMMapper.to_dto(user_update_dto)

@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_soft_delete_user(user_id: str):
    user_doc, staff_doc = g.admin.facade.admin_soft_delete_user_workflow(
        user_id,
        get_current_user_id(),
    )

    user_dto = (
        mongo_converter.doc_to_dto(
            mongo_converter.convert_ids(user_doc),
            IAMBaseDataDTO,
        )
        if user_doc
        else None
    )

    staff_dto = (
        mongo_converter.doc_to_dto(
            mongo_converter.convert_ids(staff_doc),
            StaffBaseDataDTO,
        )
        if staff_doc
        else None
    )

    return AdminUserStaffDataDTO(
        user=user_dto,
        staff=staff_dto,
    )

@admin_bp.route('/users/<user_id>/hard', methods=['DELETE'])
@role_required(["admin"])
@wrap_response
def admin_hard_delete_user(user_id):
    g.admin.user_service.admin_hard_delete_user(user_id)
    return BaseResponseDTO(
        data="User hard deleted successfully",
        message="User hard deleted successfully",
        success=True
    )

@admin_bp.route('/users/student-select', methods=['GET'])
@role_required(["admin"])
@wrap_response
def admin_list_student_select():
    students = g.admin.user_service.admin_list_student_select()
    students = mongo_converter.list_to_dto(students, AdminStudentNameSelectDTO)
    return AdminStudentNameSelectListDTO(items=students)

