import os
from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # General
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    PROJECT_NAME: str = "Code Intelligence Studio"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-codeintel-key-change-in-production-min-32-chars"

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Storage Paths (resolved relative to project root)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    WORKSPACE_ROOT: Path = BASE_DIR / "workspaces"
    ARTIFACTS_ROOT: Path = BASE_DIR / "artifacts"
    LOGS_ROOT: Path = BASE_DIR / "logs"

    # Relational Database
    DATABASE_URL: str = f"sqlite:///./data/codeintel.db"

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "codeintel_chunks"

    # GitHub
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")

    # LLM Providers
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    # Sandbox & Security
    SANDBOX_MODE: str = "subprocess"  # "docker" or "subprocess"
    SANDBOX_TIMEOUT_SECONDS: int = 60
    SANDBOX_MAX_MEMORY_MB: int = 2048

    # Token & Concurrency Budget
    DEFAULT_TOKEN_BUDGET: int = 16000
    MAX_AGENT_CONCURRENCY: int = 4


settings = Settings()
