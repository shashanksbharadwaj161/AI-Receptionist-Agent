from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = Field(
        "postgresql+asyncpg://user:password@localhost:5432/ai_receptionist", env="DATABASE_URL"
    )
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    twilio_auth_token: str = Field("", env="TWILIO_AUTH_TOKEN")
    twilio_account_sid: str = Field("", env="TWILIO_ACCOUNT_SID")
    google_credentials_path: str | None = Field(None, env="GOOGLE_CREDENTIALS_PATH")
    google_calendar_id: str | None = Field(None, env="GOOGLE_CALENDAR_ID")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
