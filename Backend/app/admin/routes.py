from app.responses import response
from app.responses.response import Response
from flask import request
from . import admin_bp
from app.auth.jwt_utils import role_required
from app.services.admin_service import get_admin_service
from app.enum.enums import Role
from app.error.exceptions import BadRequestError, NotFoundError , PydanticValidationError  # type: ignore
from app.schemas.classes import ClassCreateSchema
from app.schemas.users import AdminCreateUserSchema, AdminUpdateUserSchema
from app.dtos.users import AdminCreateUserResponseDTO , AdminUpdateUserResponseDTO , AdminFindUserResponseDTOList

from app.database.db import  get_db
from app.shared.model_utils import default_model_utils
import logging
from flask import send_from_directory # type: ignore
import os
from app.utils.auth_utils import get_current_user_id

logger = logging.getLogger(__name__)


def parse_json_body() -> dict:
    data = request.get_json()
    if not data:
        raise BadRequestError(
            message="Invalid JSON payload",
            user_message="Request body must be valid JSON.",
            details={"received": str(data)}
        )
    return data

def get_default_model_utils():
    return default_model_utils


@admin_bp.route('/users', methods=['GET'])
@role_required([Role.ADMIN.value])
def find_all_user():
    admin_service = get_admin_service(get_db())
    response: AdminFindUserResponseDTOList = admin_service.find_all_users()
    return Response.success_response(response.data.model_dump( exclude={'password'}, exclude_none=True) , message=response.message , status_code=200)



@admin_bp.route('/users', methods=['POST'])
@role_required([Role.ADMIN.value])
def admin_create_user():
    admin_id = get_current_user_id()
    utils = get_default_model_utils()
    data = parse_json_body()
    validated_admin_id = utils.validate_object_id(admin_id)
    data["created_by_admin_id"] = validated_admin_id  
    data = utils.to_model(data, AdminCreateUserSchema)
    admin_service = get_admin_service(get_db())
    response: AdminCreateUserResponseDTO = admin_service.admin_create_user(data)
    return Response.success_response(
        data=response.data.model_dump(exclude={'password'}, exclude_none=True),
        message=response.message,
        status_code=201
    )
    


@admin_bp.route('/users/<_id>', methods=['PUT'])
@role_required([Role.ADMIN.value])
def admin_update_user(_id):
    """
    Edit an existing user (Admin only).
    """
    admin_id = get_current_user_id()
    utils = get_default_model_utils()
    data = parse_json_body()
    validated_admin_id = utils.validate_object_id(admin_id)
    data['updated_by_admin_id'] = validated_admin_id
    user_id = utils.validate_object_id(_id)
    data = utils.to_model(data, AdminUpdateUserSchema)
    admin_service = get_admin_service(get_db())
    updated_user: AdminUpdateUserResponseDTO = admin_service.admin_update_user(user_id, data)
    user_data = updated_user.data.model_dump(exclude={'password'}, exclude_none=True)
    return Response.success_response(
        data=user_data,
        message=updated_user.message,
        status_code=200
    )




@admin_bp.route('/users/<_id>', methods=['DELETE'])
@role_required([Role.ADMIN.value])
def admin_delete_user(_id):
    admin_service = get_admin_service(get_db())
    admin_service.admin_delete_user(_id)
    return Response.success_response(message="User deleted successfully")


@admin_bp.route('/classes', methods=['GET'])
@role_required([Role.ADMIN.value])
def find_all_classes():
    admin_service = get_admin_service(get_db())
    response: AdminFindClassResponseDTOList = admin_service.find_all_classes()
    return Response.success_response(response.data.model_dump(exclude_none=True) , message=response.message , status_code=200)



@admin_bp.route('/classes', methods=['POST'])
@role_required([Role.ADMIN.value])
def create_class():
    utils = get_default_model_utils()
    admin_service = get_admin_service(get_db())
    data = parse_json_body()
    validated_admin_id = utils.validate_object_id(get_current_user_id())
    data = utils.to_model(data, ClassCreateSchema)
    response: AdminCreateClassResponseDTO = admin_service.admin_create_class(data, validated_admin_id )
    return Response.success_response(
        data=response.data.model_dump(exclude_none=True),
        message=response.message,
        status_code=201
    )












@admin_bp.route('/find-one-user', methods=['POST'])
@role_required([Role.ADMIN.value])
def find_one_user():
    """
    Find a user by ID, username, or email (Admin only).
    """
    data = parse_json_body()
    admin_service = get_admin_service(get_db())
    user = None
    _id = data.get("id") or data.get("_id")

    if _id:
        user = admin_service.user_repo.find_user_by_id(str(_id))
    elif "username" in data:
        user = admin_service.user_repo.find_user_by_username(data["username"])
    elif "email" in data:
        user = admin_service.user_repo.find_user_by_email(data["email"])
    else:
        raise BadRequestError(
            message="No valid identifier provided",
            user_message="Please provide 'id', 'username', or 'email'.",
            details={"fields_checked": ["id", "username", "email"]}
        )
    if not user:
        raise NotFoundError(
            message="User not found",
            resource_type="User",
            resource_id=_id or data.get("username") or data.get("email")
        )

    user_data = UserDetailResponseSchema.model_validate(
        user, by_alias=True
    )
    user_data = user_data.model_dump(by_alias=True, exclude_none=True)
    return Response.success_response(user_data, message="User fetched successfully")


@admin_bp.route('/count-by-role', methods=['GET'])
@role_required([Role.ADMIN.value])
def count_users_by_role():
    """
    Count users by role (Admin only).
    """
    admin_service = get_admin_service(get_db())
    counts = admin_service.user_repo.count_users_by_role()
    return Response.success_response(counts, message="User counts by role fetched successfully")

@admin_bp.route('/growth-stats', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_user_growth_stats():
    """
    Get user growth statistics (Admin only).
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not start_date or not end_date:
        raise BadRequestError(
            message="Missing start_date or end_date query parameters",
            user_message="Please provide both 'start_date' and 'end_date' as query parameters.",
            details={"missing": [k for k in ['start_date', 'end_date'] if not request.args.get(k)]}
        )
    admin_service = get_admin_service(get_db())
    stats = admin_service.user_repo.find_user_growth_stats(start_date=start_date, end_date=end_date)
    return Response.success_response(stats, message="User growth statistics fetched successfully")


@admin_bp.route('/users/growth-stats-by-role', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_user_growth_stats_by_role():
    """
    Get user growth statistics by role (Admin only).
    """
    current_start_date = request.args.get('current_start_date')
    current_end_date = request.args.get('current_end_date')
    previous_start_date = request.args.get('previous_start_date')
    previous_end_date = request.args.get('previous_end_date')

    missing_current = [k for k in ['current_start_date', 'current_end_date'] if not request.args.get(k)]
    missing_previous = [k for k in ['previous_start_date', 'previous_end_date'] if not request.args.get(k)]

    if missing_current:
        raise BadRequestError(
            message="Missing current period date query parameters",
            user_message=f"Please provide {', '.join(missing_current)} as query parameters.",
            details={"missing": missing_current}
        )
    if missing_previous:
        raise BadRequestError(
            message="Missing previous period date query parameters",
            user_message=f"Please provide {', '.join(missing_previous)} as query parameters.",
            details={"missing": missing_previous}
        )

    admin_service = get_admin_service(get_db())
    stats = admin_service.user_repo.find_users_growth_stats_by_role_with_comparison(
        current_start_date=current_start_date,
        current_end_date=current_end_date,
        previous_start_date=previous_start_date,
        previous_end_date=previous_end_date,
    )
    return Response.success_response(stats, message="User growth statistics fetched successfully")



@admin_bp.route('/users/detail/<_id>', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_user_detail(_id):
    """Get detailed information about a user by ID (Admin only)."""
    if not _id:
        raise BadRequestError(message="User ID is required", user_message="User ID is required.")
    admin_service = get_admin_service(get_db())
    user = admin_service.user_repo.find_user_detail(_id)
    if not user:
        raise NotFoundError(message=f"User not found with ID {_id}", user_message="User not found.")
    
    return Response.success_response(user, message="User details fetched successfully", status_code=200)


@admin_bp.route('/users/edit-user-detail/<_id>', methods=['PATCH'])
@role_required([Role.ADMIN.value])
def patch_user_detail(_id):
    """
    Edit user detail (Admin only).
    """
    if not _id:
        raise BadRequestError(message="User ID is required", user_message="User ID is required.")
    data = parse_json_body()
    # Optional: validate data schema here if you have UserPatchUserDetailSchema
    # For example:
    # try:
    #     user_update = UserPatchUserDetailSchema.model_validate(data)
    # except ValidationError as ve:
    #     raise ValidationError(message=f"Validation error: {ve}", user_message="Invalid input data.")
    user_update = data  # If you do validation above, use user_update.model_dump()

    admin_service = get_admin_service(get_db())
    updated_user = admin_service.patch_user_detail(_id, user_update)
    return Response.success_response(updated_user, message="User detail updated successfully")


@admin_bp.route('/users/search-user', methods=['POST'])
@role_required([Role.ADMIN.value])
def search_user():
    """Search for users by username or email (Admin only)."""
    
    data = parse_json_body()
    
    query = data.get('query', '').strip()
    page = data.get('page', 1)
    page_size = data.get('page_size', 10)
    
    # Optional: Validate page and page_size are positive integers
    if not (isinstance(page, int) and page > 0):
        raise PydanticValidationError(message="Page must be a positive integer.", user_message="Invalid page number.")
    if not (isinstance(page_size, int) and 0 < page_size <= 100):
        raise PydanticValidationError(message="Page size must be between 1 and 100.", user_message="Invalid page size.")

    admin_service = get_admin_service(get_db())
    users = admin_service.user_repo.search_user(query, page, page_size)
    users_serialized = [
        user.model_dump(mode="json", by_alias=True, exclude_none=True) for user in users
    ]
    
    return Response.success_response(users_serialized, message="Users fetched successfully")
















@admin_bp.route('/openapi.yaml', methods=['GET'])
def get_openapi_yaml():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')
