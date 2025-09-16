
from werkzeug.security import generate_password_hash, check_password_hash
from app.contexts.iam.data_transfer.responses import UserResponseDataDTO
from app.contexts.auth.jwt_utils import create_access_token
from datetime import timedelta



class AuthService:
    def hash_password(self, password: str) -> str:
        return generate_password_hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return check_password_hash(hashed_password, plain_password)

    def create_access_token(self, user_data: dict) -> str:
        payload = {
            "id": str(user_data["id"]),
            "role": user_data["role"],
            "username": user_data["username"],
            "email": user_data["email"],
        }
        return create_access_token(data=payload, expire_delta=timedelta(hours=1))




def get_auth_service() -> AuthService:
    return AuthService()