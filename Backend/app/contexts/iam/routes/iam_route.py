from flask import Blueprint, request, make_response, jsonify

from app.contexts.infra.database.db import get_db
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.shared.decorators.response_decorator import wrap_response

from app.contexts.iam.services.iam_service import IAMService
from app.contexts.iam.mapper.iam_mapper import IAMMapper

from app.contexts.iam.data_transfer.request import (
    IAMLoginSchema,
    IAMUpdateSchema,
    PasswordResetConfirmSchema,
)
from app.contexts.iam.data_transfer.response import IAMResponseDataDTO

from app.contexts.iam.auth.cookies import set_refresh_cookie, clear_refresh_cookie
from app.contexts.iam.auth.jwt_utils import login_required
from app.contexts.core.security.auth_utils import get_current_user

from app.contexts.iam.auth.refresh_utils import (
    create_refresh_token,
    hash_refresh_token,
    now_utc,
    REFRESH_TTL,
)


iam_bp = Blueprint("iam_bp", __name__)


# -------------------------
# AUTH: LOGIN
# -------------------------
@iam_bp.route("/login", methods=["POST"])
def login_user():
    user_service = IAMService(get_db())
    user_schema: IAMLoginSchema = pydantic_converter.convert_to_model(request.json, IAMLoginSchema)

    dto, refresh = user_service.login(user_schema.email, user_schema.password)

    # dto is Pydantic model (IAMResponseDataDTO)
    resp: IAMResponseDataDTO = make_response(jsonify(dto.model_dump()))
    set_refresh_cookie(resp, refresh)
    return resp


# -------------------------
# AUTH: LOGOUT
# -------------------------

@iam_bp.route("/logout", methods=["POST"])
def logout_user():
    db = get_db()
    user_service = IAMService(db)

    rt = request.cookies.get("refresh_token") or ""
    user_service.logout(rt)

    resp = make_response(jsonify({"message": "Logged out"}))
    clear_refresh_cookie(resp)   
    return resp

# -------------------------
# AUTH: REFRESH (ROTATE)
# -------------------------
@iam_bp.route("/refresh", methods=["POST"])
def refresh_access_token():
    db = get_db()
    refresh_tokens = db["refresh_tokens"]

    rt = request.cookies.get("refresh_token")
    if not rt:
        return jsonify({"msg": "Missing refresh token"}), 401

    rt_hash = hash_refresh_token(rt)
    doc = refresh_tokens.find_one({"token_hash": rt_hash})
    if not doc:
        return jsonify({"msg": "Invalid refresh token"}), 401

    if doc.get("revoked_at") is not None:
        return jsonify({"msg": "Refresh token revoked"}), 401

    if doc["expires_at"] < now_utc():
        return jsonify({"msg": "Refresh token expired"}), 401

    iam_service = IAMService(db)

    raw_user = iam_service._iam_read_model.get_by_id(doc["user_id"])
    if not raw_user:
        return jsonify({"msg": "User not found"}), 401

    iam_model = iam_service._iam_mapper.to_domain(raw_user)
    safe_dict = iam_service._iam_mapper.to_safe_dict(iam_model)

    # Rotate refresh token
    new_rt = create_refresh_token()
    new_hash = hash_refresh_token(new_rt)

    refresh_tokens.update_one(
        {"_id": doc["_id"]},
        {"$set": {"revoked_at": now_utc(), "replaced_by_hash": new_hash}},
    )

    refresh_tokens.insert_one(
        {
            "user_id": str(safe_dict["id"]),
            "token_hash": new_hash,
            "created_at": now_utc(),
            "expires_at": now_utc() + REFRESH_TTL,
            "revoked_at": None,
            "replaced_by_hash": None,
        }
    )

    access = iam_service._auth_service.create_access_token(safe_dict)

    resp = make_response(jsonify({"access_token": access}))
    set_refresh_cookie(resp, new_rt)
    return resp


# -------------------------
# PROFILE: GET ME
# -------------------------
@iam_bp.route("/me", methods=["GET"])
@wrap_response
@login_required()
def get_me():
    user_service = IAMService(get_db())
    current = get_current_user()  
    me_dto = user_service.me(current["user_id"])
    return me_dto


# -------------------------
# PROFILE: UPDATE ME (email/username)
# -------------------------
@iam_bp.route("/me", methods=["PATCH"])
@wrap_response
@login_required()
def patch_me():
    user_service = IAMService(get_db())
    current = get_current_user()
    payload: IAMUpdateSchema = pydantic_converter.convert_to_model(request.json, IAMUpdateSchema)
    iam_domain = user_service.update_info(current["user_id"], payload, update_by_admin=False)
    return IAMMapper.to_dto(iam_domain)

# -------------------------
# PASSWORD: CHANGE (LOGGED IN)
# -------------------------
@iam_bp.route("/change-password", methods=["POST"])
@wrap_response
@login_required()
def change_password():
    user_service = IAMService(get_db())
    current = get_current_user()

    body = request.json or {}
    current_pw = str(body.get("current_password") or "")
    new_pw = str(body.get("new_password") or "")
    return user_service.change_password(current["user_id"], current_pw, new_pw)

# -------------------------
# RESET PASSWORD: CONFIRM (TOKEN-BASED)
# -------------------------
@iam_bp.route("/reset-password/confirm", methods=["POST"])
@wrap_response
def confirm_password_reset():
    user_service = IAMService(get_db())
    payload: PasswordResetConfirmSchema = pydantic_converter.convert_to_model(
        request.json, PasswordResetConfirmSchema
    )
    return user_service.confirm_password_reset(payload.token, payload.new_password)