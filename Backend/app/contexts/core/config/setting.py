import os
from dotenv import load_dotenv
from typing import Optional, List

from app.contexts.core.errors.app_base_exception import handle_exception

load_dotenv()


def _parse_csv(value: str) -> List[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


class Settings:
    def __init__(self):
        self.DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret")
        self.DATABASE_URI: str = os.getenv("DATABASE_URI", "mongodb://localhost:27017")

        self.GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_DISCOVERY_URL: str = (
            "https://accounts.google.com/.well-known/openid-configuration"
        )

        self.TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

        self.DEBUG_TB_INTERCEPT_REDIRECTS: bool = False
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

        self.FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

        raw_origins = os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        )
        self.CORS_ALLOWED_ORIGINS: List[str] = _parse_csv(raw_origins)


        if self.FRONTEND_URL and self.FRONTEND_URL not in self.CORS_ALLOWED_ORIGINS:
            self.CORS_ALLOWED_ORIGINS.append(self.FRONTEND_URL)

        self._validate()

    def _validate(self):
        enable_google_oauth = os.getenv("ENABLE_GOOGLE_OAUTH", "false").lower() == "true"
        if enable_google_oauth and (not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET):
            raise handle_exception(
                ValueError("Google Client ID and Secret must be set when ENABLE_GOOGLE_OAUTH=true.")
            )


settings = Settings()