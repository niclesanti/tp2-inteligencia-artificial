from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_session_ttl: int = 1800
    backend_url: str = "http://backend:8080"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = "https://cloud.langfuse.com"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
