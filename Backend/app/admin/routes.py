
from flask import request
from . import admin_bp
from app.auth.jwt_utils import role_required
from app.services.user_service import get_user_service
from app.enums.roles import Role
from app.error.exceptions import BadRequestError, NotFoundError , PydanticValidationError  # type: ignore
from app.responses.response import Response 
from app.schemas.user_schema import UserCreateSchema, UserResponseSchema, UserPatchSchema, UserPatchUserDetailSchema, UserDetailResponseSchema
from app.database.db import  get_db
import logging
from flask import send_from_directory , g # type: ignore
from  functools import wraps
import os
logger = logging.getLogger(__name__)

def with_user_service(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.user_service = get_user_service(get_db())
        return func(*args, **kwargs)
    return wrapper

def parse_json_body() -> dict:
    data = request.get_json()
    if not data:
        raise BadRequestError(
            message="Invalid JSON payload",
            user_message="Request body must be valid JSON.",
            details={"received": str(data)}
        )
    return data

@admin_bp.route('/', methods=['GET'])
@with_user_service
@role_required([Role.ADMIN.value])
def get_all_users():
    """
    Fetch all users (Admin only).
    """
    users = g.user_service.user_repo.find_all_users()
    if not users:
        return Response.success_response(data=[], message="No users found")
    user_data = [
        user.model_dump(exclude={"password"}, by_alias=True)
        for user in users
    ]
    return Response.success_response(data=user_data, message="Users fetched successfully")



@admin_bp.route('/users', methods=['POST'])
@with_user_service
def create_user():
    """
    Create a new user (Admin only).
    """
    data = parse_json_body()
    user = g.user_service.create_user(data)
    user_response = UserResponseSchema.model_validate(user)
    return Response.success_response(
        user_response.model_dump(by_alias=True),
        message="Successfully created user",
        status_code=201
    )

@admin_bp.route('/users/<_id>', methods=['PATCH'])
@with_user_service
@role_required([Role.ADMIN.value])
def patch_user(_id):
    """
    Edit an existing user (Admin only).
    """
    data = parse_json_body()


    updated_user = g.user_service.patch_user(_id, data)

    if not updated_user:
        raise NotFoundError(
            message="User not found or update failed",
            resource_type="User",
            resource_id=_id
        )

    user_model = UserResponseSchema.model_validate(updated_user)
    user_data = user_model.model_dump(by_alias=True, exclude_none=True)

    return Response.success_response(
        user_data,
        message="User updated successfully"
    )




@admin_bp.route('/users/<_id>', methods=['DELETE'])
@role_required([Role.ADMIN.value])
@with_user_service
def delete_user(_id):
    """
    Delete a user by ID (Admin only).
    """
    result = g.user_service.delete_user(_id)

    if not result:
        raise NotFoundError(
            message="User not found or delete failed",
            resource_type="User",
            resource_id=_id
        )

    return Response.success_response(message="User deleted successfully")


@admin_bp.route('/users/find-one-user', methods=['POST'])
@role_required([Role.ADMIN.value])
@with_user_service
def find_one_user():
    """
    Find a user by ID, username, or email (Admin only).
    """
    data = parse_json_body()
    user = None
    _id = data.get("id") or data.get("_id")

    if _id:
        user = g.user_service.user_repo.find_user_by_id(str(_id))
    elif "username" in data:
        user = g.user_service.user_repo.find_user_by_username(data["username"])
    elif "email" in data:
        user = g.user_service.user_repo.find_user_by_email(data["email"])
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


@admin_bp.route('/users/count-by-role', methods=['GET'])
@role_required([Role.ADMIN.value])
@with_user_service
def count_users_by_role():
    """
    Count users by role (Admin only).
    """
    counts = g.user_service.user_repo.count_users_by_role()
    return Response.success_response(counts, message="User counts by role fetched successfully")

@admin_bp.route('/users/growth-stats', methods=['GET'])
@role_required([Role.ADMIN.value])
@with_user_service
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
    stats = g.user_service.user_repo.find_user_growth_stats(start_date=start_date, end_date=end_date)
    return Response.success_response(stats, message="User growth statistics fetched successfully")


@admin_bp.route('/users/growth-stats-by-role', methods=['GET'])
@role_required([Role.ADMIN.value])
@with_user_service
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

    stats = g.user_service.user_repo.find_users_growth_stats_by_role_with_comparison(
        current_start_date=current_start_date,
        current_end_date=current_end_date,
        previous_start_date=previous_start_date,
        previous_end_date=previous_end_date,
    )
    return Response.success_response(stats, message="User growth statistics fetched successfully")



@admin_bp.route('/users/detail/<_id>', methods=['GET'])
@role_required([Role.ADMIN.value])
@with_user_service
def get_user_detail(_id):
    """Get detailed information about a user by ID (Admin only)."""
    if not _id:
        raise BadRequestError(message="User ID is required", user_message="User ID is required.")
    user = g.user_service.user_repo.find_user_detail(_id)
    if not user:
        raise NotFoundError(message=f"User not found with ID {_id}", user_message="User not found.")
    
    return Response.success_response(user, message="User details fetched successfully", status_code=200)


@admin_bp.route('/users/edit-user-detail/<_id>', methods=['PATCH'])
@role_required([Role.ADMIN.value])
@with_user_service
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

    updated_user = g.user_service.patch_user_detail(_id, user_update)
    return Response.success_response(updated_user, message="User detail updated successfully")


@admin_bp.route('/users/search-user', methods=['POST'])
@role_required([Role.ADMIN.value])
@with_user_service
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

    users = g.user_service.user_repo.search_user(query, page, page_size)
    users_serialized = [
        user.model_dump(mode="json", by_alias=True, exclude_none=True) for user in users
    ]
    
    return Response.success_response(users_serialized, message="Users fetched successfully")
















@admin_bp.route('/openapi.yaml', methods=['GET'])
def get_openapi_yaml():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')
