from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

# 配置类

class Settings(BaseSettings):
    llm_api_key: str
    llm_base_url: str
    llm_model: str

    embedding_provider: str = "dashscope"
    embedding_model: str = "text-embedding-v2"
    embedding_dimensions: int = 1536
    dashscope_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
