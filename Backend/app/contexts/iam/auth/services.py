
from werkzeug.security import generate_password_hash, check_password_hash
from app.contexts.iam.auth.jwt_utils import create_access_token
from datetime import timedelta
from app.contexts.core.config.setting import settings



class AuthService:
    @staticmethod
    def _access_token_ttl_minutes() -> int:
        raw = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 15)
        try:
            minutes = int(raw)
        except (TypeError, ValueError):
            return 15
        return minutes if minutes > 0 else 15

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
            "type": "access",
        }
        return create_access_token(
            data=payload,
            expire_delta=timedelta(minutes=self._access_token_ttl_minutes()),
        )


def get_auth_service() -> AuthService:
    return AuthService()
