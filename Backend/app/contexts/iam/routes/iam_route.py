from flask import Blueprint ,request
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.iam.services.iam_service import IAMService
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.infra.database.db import get_db
from app.contexts.iam.data_transfer.request import  IAMUpdateSchema , IAMLoginSchema
from app.contexts.iam.data_transfer.response import IAMResponseDataDTO , IAMUpdateDataDTO
from app.contexts.iam.domain.iam import IAM
from app.contexts.iam.mapper.iam_mapper import IAMMapper
iam_bp = Blueprint('iam_bp', __name__)




# -------------------------
# Authentication routes
# -------------------------
@iam_bp.route('/login', methods=['POST'])
@wrap_response
def login_user():
    user_service = IAMService(get_db())
    user_schema: IAMLoginSchema = pydantic_converter.convert_to_model(request.json, IAMLoginSchema)
    user_dto: IAMResponseDataDTO = user_service.login(user_schema.email, user_schema.password)
    return user_dto


# -------------------------
# Profile routes
# -------------------------
@iam_bp.route('/update_info', methods=['PATCH'])
@wrap_response
def update_user_profile():
    user_service = IAMService(get_db())
    current_user_id = request.user_id 
    update_schema: IAMUpdateSchema = pydantic_converter.convert_to_model(request.json, IAMUpdateSchema)
    iam_domain: IAM = user_service.update_info(current_user_id, update_schema , update_by_admin=False)
    return IAMMapper.to_dto(iam_domain)


