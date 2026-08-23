import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Third-party credentials
    TURNSTILE_SECRET_KEY: str = ""
    RESEND_API_KEY: str = ""
    CONTACT_EMAIL_TO: str = ""
    FROM_EMAIL: str = "Signal Website <onboarding@resend.dev>"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./signal.db"  # Defaulting to sqlite for ease of local dev if postgres isn't setup

    # JWT Authentication
    JWT_SECRET_KEY: str = "your_super_secret_jwt_key_here"  # Overwrite in .env
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI Agents
    OPENROUTER_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
