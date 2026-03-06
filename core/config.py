from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # =========================
    # 🔐 Security
    # =========================
    SECRET_KEY: str
    PASSWORD_PEPPER: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ======================
    # Rate Limiting
    # ======================
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_WINDOW_SECONDS: int = 300   # 5 minutes

    REGISTER_MAX_ATTEMPTS: int = 3
    REGISTER_WINDOW_SECONDS: int = 600  # 10 minutes
    # =========================
    # ⚙️ App Settings
    # =========================
    DEBUG: bool = False
    STORAGE_BACKEND: str = "sqlalchemy"

    # =========================
    # data base postgresql
    # =========================

    DATABASE_URL:str 
    
    # =========================
    # 📁 Load from .env
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",)#ignore unknow env vars safely
    
# Cache settings (important for performance)
@lru_cache
def get_settings() -> Settings:
    return Settings()  # Return an instance of Settings class
