from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# 配置类

class Settings(BaseSettings):
    llm_api_key: str
    llm_base_url: str
    llm_model: str

    order_storage_backend: Literal["demo", "postgres"] = "demo"

    postgres_host: str = "localhost"
    postgres_port: int = 25432
    postgres_db: str = "agent_learning"
    postgres_user: str = "learner"
    postgres_password: SecretStr | None = None

    embedding_provider: str = "dashscope"
    embedding_model: str = "text-embedding-v2"
    embedding_dimensions: int = 1536
    dashscope_api_key: str | None = None

    knowledge_retrieval_backend: Literal["pgvector", "ngram"] = "ngram"
    pgvector_top_k: int = Field(default=3, ge=1, le=20)
    pgvector_min_score: float = Field(default=0.5, ge=0.0, le=1.0)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
