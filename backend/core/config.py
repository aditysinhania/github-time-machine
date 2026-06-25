from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/github_time_machine"

    # GitHub
    GITHUB_TOKEN: str = ""

    # AI
    AI_PROVIDER: str = "groq"  # "gemini" or "openai"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # App
    SECRET_KEY: str = "dev-secret-change-in-prod"
    ENVIRONMENT: str = "development"
    REPO_CLONE_DIR: str = "/tmp/repos"
    MAX_COMMITS: int = 1000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @field_validator("AI_PROVIDER")
    @classmethod
    def validate_ai_provider(cls, v: str) -> str:
        if v not in ("gemini", "openai", "groq"):
            raise ValueError("AI_PROVIDER must be 'gemini' or 'openai' or 'groq'")
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
