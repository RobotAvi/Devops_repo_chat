from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    gitlab_base_url: str = Field(default="https://gitlab.com/api/v4", alias="GITLAB_BASE_URL")
    gitlab_token: str = Field(default="", alias="GITLAB_TOKEN")

    # Chat LLM (OpenAI-compatible, e.g. vLLM)
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")

    # Embeddings (OpenAI-compatible). Defaults to OpenAI if explicit vars not set
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    embedding_api_key: str = Field(default="", alias="EMBEDDING_API_KEY")
    embedding_base_url: str | None = Field(default=None, alias="EMBEDDING_BASE_URL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    cache_dir: str = Field(default="./data", alias="CACHE_DIR")
    cache_ttl_seconds: int = Field(default=86400, alias="CACHE_TTL_SECONDS")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    index_dir: str = Field(default="./indices", alias="INDEX_DIR")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    fastapi_host: str = Field(default="0.0.0.0", alias="FASTAPI_HOST")
    fastapi_port: int = Field(default=8000, alias="FASTAPI_PORT")

    allowed_projects: str = Field(default="", alias="ALLOWED_PROJECTS")
    admin_tokens: str = Field(default="", alias="ADMIN_TOKENS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # singleton-like convenience

