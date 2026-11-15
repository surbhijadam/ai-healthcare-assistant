import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application & Environment
    PROJECT_NAME: str = "AI Healthcare Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security & Authentication
    SECRET_KEY: str = "change_this_to_a_super_secure_random_hex_string_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # PostgreSQL & pgvector Database Connection
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/healthcare_db"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/healthcare_db"

    # Groq API Configuration
    GROQ_API_KEY: str = "mock_groq_api_key_for_development"
    GROQ_MODEL: str = "qwen/qwen3.8-27b"

    # Sentence-Transformers Embedding Model
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Frontend & Network
    FRONTEND_PORT: int = 8501
    BACKEND_PORT: int = 8000
    BACKEND_API_BASE_URL: str = "http://localhost:8000/api/v1"

    # CORS Allowed Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # File Storage Paths
    UPLOAD_DIR: str = "./backend/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Emergency Triage Keywords (for immediate clinical safety alert)
    EMERGENCY_KEYWORDS: List[str] = [
        "chest pain",
        "heart attack",
        "shortness of breath",
        "difficulty breathing",
        "severe bleeding",
        "stroke",
        "facial droop",
        "slurred speech",
        "loss of consciousness",
        "unconscious",
        "suicide",
        "overdose",
        "anaphylaxis",
        "crushing pressure",
    ]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
