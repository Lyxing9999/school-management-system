from flask import Blueprint ,request
from app.contexts.iam.data_transfer.requests import UserRegisterSchema, UserUpdateSchema , UserLoginSchema
from app.contexts.shared.model_converter import converter_utils
from app.contexts.iam.services import IAMService
from app.contexts.shared.decorators.wrap_response import wrap_response
from app.contexts.infra.database.db import get_db
from app.contexts.iam.data_transfer.responses import UserResponseDataDTO , UserLoginDataDTO , UserRegisterDataDTO
from app.contexts.common.base_response_dto import BaseResponseDTO
iam_bp = Blueprint('iam_bp', __name__)




# -------------------------
# Authentication routes
# -------------------------
@iam_bp.route('/login', methods=['POST'])
@wrap_response
def login_user():
    user_service = IAMService(get_db())
    user_schema = converter_utils.convert_to_model(request.json, UserLoginSchema)
    user_model, token = user_service.login_user(user_schema.email, user_schema.password)
    user_dto = UserResponseDataDTO(**user_service.to_safe_dict(user_model))
    login_dto = UserLoginDataDTO(user=user_dto, access_token=token)
    return BaseResponseDTO(data=login_dto, message="User logged in", success=True)




@iam_bp.route('/register', methods=['POST'])
@wrap_response
def register_user_route():
    user_service = IAMService(get_db())
    register_schema: UserRegisterSchema = converter_utils.convert_to_model(request.json, UserRegisterSchema)
    user_model, token = user_service.register_user(register_schema)
    user_dto = UserResponseDataDTO(**user_service.to_safe_dict(user_model))
    return BaseResponseDTO(
        data=UserRegisterDataDTO(user=user_dto, access_token=token),
        message="User registered successfully",
        success=True
    )


# -------------------------
# Profile routes
# -------------------------
@iam_bp.route('/profile', methods=['PATCH'])
@wrap_response
def update_user_profile():
    user_service = IAMService(get_db())
    current_user_id = request.user_id 
    update_schema: UserUpdateSchema = converter_utils.convert_to_model(request.json, UserUpdateSchema)
    updated_user: User = user_service.update_profile(current_user_id, update_schema , update_by_admin=False)
    user_dto = UserResponseDataDTO(**user_service.to_safe_dict(updated_user))
    return BaseResponseDTO(data=user_dto, message="User updated successfully", success=True)


