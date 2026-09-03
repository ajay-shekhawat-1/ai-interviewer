from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    app_name: str = "AI Interviewer API"
    app_version: str = "1.0.0"
    environment: str = "development"

    frontend_url: str = "http://localhost:5173"

    # Groq configuration
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"

    # Resume upload configuration
    max_resume_size_mb: int = 5

    # MySQL database configuration
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "ai_interviewer"
    db_user: str = "root"
    db_password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached application settings instance.
    """

    return Settings()