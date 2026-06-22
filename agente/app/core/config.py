from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_session_ttl: int = 1800
    backend_url: str = "http://backend:8080"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = "https://cloud.langfuse.com"

    # ─── RAG ─────────────────────────────────────────────────────
    qdrant_collection_name: str = "guias_financieras"
    embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384
    rag_top_k: int = 5
    rag_chunk_size: int = 2000          # caracteres (~500 tokens por chunk)
    docs_rag_dir: str = "docs RAG"      # relativo a la raíz de /agente/

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
