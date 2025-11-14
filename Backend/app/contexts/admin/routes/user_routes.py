from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.admin.data_transfer.requests import AdminCreateUserSchema, AdminUpdateUserSchema
from app.contexts.admin.data_transfer.responses import (
    AdminCreateUserDataDTO, AdminUpdateUserDataDTO, PaginatedUsersDataDTO
)
from app.contexts.common.base_response_dto import BaseResponseDTO


@admin_bp.route("/users", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_users_paginated():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 5))
    roles = request.args.getlist("role[]") or request.args.getlist("role")
    users_list, total = g.admin_facade.user_service.admin_get_users(
        roles, page=page, page_size=page_size
    )
    
    return PaginatedUsersDataDTO(
        users=users_list,
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
    user_response_dto = g.admin_facade.user_service.admin_create_user(
        user_schema, created_by=admin_id
    )
    return AdminCreateUserDataDTO(**user_response_dto.model_dump())
    

@admin_bp.route('/users/<user_id>', methods=['PATCH'])
@role_required(["admin"])
@wrap_response
def admin_update_user(user_id):
    user_schema = pydantic_converter.convert_to_model(request.json, AdminUpdateUserSchema)
    user_update_dto = g.admin_facade.user_service.admin_update_user(user_id, user_schema)
    return AdminUpdateUserDataDTO(**user_update_dto.model_dump())


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@role_required(["admin"])
@wrap_response
def admin_soft_delete_user(user_id):
    g.admin_facade.user_service.admin_soft_delete_user(user_id)
    return BaseResponseDTO(
        data="User deleted successfully",
        message="User deleted successfully",
        success=True
    )


@admin_bp.route('/users/<user_id>/hard', methods=['DELETE'])
@role_required(["admin"])
@wrap_response
def admin_hard_delete_user(user_id):
    g.admin_facade.user_service.admin_hard_delete_user(user_id)
    return BaseResponseDTO(
        data="User hard deleted successfully",
        message="User hard deleted successfully",
        success=True
    )