import os
from dotenv import load_dotenv  
from typing import Optional
from app.contexts.core.error.app_base_exception import handle_exception



load_dotenv()


class Settings:
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret")
    DATABASE_URI: str = os.getenv("DATABASE_URI", "mongodb://localhost:27017")
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL: str = "https://accounts.google.com/.well-known/openid-configuration"
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    DEBUG_TB_INTERCEPT_REDIRECTS: bool = False
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    def __post_init__(self):
        if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET:
            raise handle_exception(ValueError(
                "Google Client ID and Secret must be set in environment variables."
            ))


settings = Settings()