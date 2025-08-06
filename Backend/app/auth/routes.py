
from flask import request, url_for  # type: ignore
from datetime import timedelta
from app.enum.enums import Role
from . import auth_bp
from app import oauth
from app.services.user_service import get_user_service
from app.database.db import get_db
import logging
from app.responses.response import Response
from app.schemas.users.user_register_schema import UserRegisterSchema
from app.schemas.users.user_login_schema import UserLoginSchema
logger = logging.getLogger(__name__)
from app.shared.model_utils import default_model_utils



@auth_bp.route('/google/login')
def google_login():
    """Redirect to Google OAuth."""
    redirect_uri = url_for('auth.google_login_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/google/login/callback')
def google_login_callback():
    """Handle Google login callback."""
    token = oauth.google.authorize_access_token()
    nonce = token.get('nonce')
    user_info = oauth.google.parse_id_token(token, nonce=nonce)
    email = user_info.get('email')

    if not email:
        return Response.error_response("Google login failed, no email found", status_code=400)

    user_service = get_user_service(get_db())
    user = user_service.user_repo.find_user_by_email(email)

    if user:
        if user.role != Role.STUDENT.value:
            return Response.forbidden_response("Google login is only allowed for student accounts")
    else:
        user_data = {
            'username': user_info.get('name', email.split('@')[0]),
            'email': email,
            'role': Role.STUDENT.value,
            'password': "",
            'google_id': user_info.get('sub')
        }
        result = user_service.create_user(user_data)
        if not result:
            return Response.error_response("User registration failed", status_code=500)
        user = result.get("user")
        if not user:
            return Response.error_response("User registration failed", status_code=500)

    access_token = create_access_token(
        data=build_jwt_payload(user),
        expire_delta=timedelta(hours=1)
    )

    return Response.success_response({"access_token": access_token}, message="Login successful")


@auth_bp.route('/register', methods=['POST'])
def register():
    utils = default_model_utils
    user_service = get_user_service(get_db())

    print(request.get_json())
    user_schema = utils.to_model(request.get_json(), UserRegisterSchema)
    user_dto = user_service.register_user(user_schema)  
    return Response.success_response(
        data=user_dto.data.model_dump(), 
        message=user_dto.message,
        status_code=201
    )







@auth_bp.route('/login', methods=['POST'])
def login():
    utils = default_model_utils
    user_service = get_user_service(get_db())
    user_schema = utils.to_model(request.get_json(), UserLoginSchema)
    user = user_service.login_user(user_schema)
    return Response.success_response(
        data=user.data.model_dump(), 
        message=user.message,
        status_code=200
    )



@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (no server state for JWT)."""
    return Response.success_response(message="Successfully logged out")
