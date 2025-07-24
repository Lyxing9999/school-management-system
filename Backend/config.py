
import os
from dotenv import load_dotenv # type: ignore
from typing import Optional
from app.error.exceptions import handle_exception
load_dotenv() 

class Config:
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret")
    DATABASE_URI: str = os.getenv("DATABASE_URI", "mongodb://localhost:27017")
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    DEBUG_TB_INTERCEPT_REDIRECTS = False    
    if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
        raise handle_exception(ValueError("Google Client ID and Secret must be set in environment variables."))