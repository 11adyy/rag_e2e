from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

ENV_FILE_PATH = PROJECT_ROOT / ".env"

class Settings(BaseSettings):

    EMBEDDINGS_MODEL: str = "text-embedding-3-small"
    OPENAI_API_KEY: str = ""
    BASE_URL: str = "https://api.fireworks.ai/inference/v1/"

    RAG_CHROMA_PERSIST_DIR: str = str(PROJECT_ROOT / "src" / "chatbot" / "chroma_db")
    RAG_HNSW_M: int = 16
    RAG_HNSW_EF_CONSTRUCTION: int = 200
    RAG_HNSW_EF_SEARCH: int = 50


    RAG_CHUNK_SIZE: int = Field(default=500, ge=1)
    RAG_CHUNK_OVERLAP: int = 50


    TO_INDEX_PATH: str = str(PROJECT_ROOT / "src" / "chatbot" / "data" / "to_index")
    INDEXED_PATH: str = str(PROJECT_ROOT / "src" / "chatbot" / "data" / "indexed")


    DENSE_RETRIEVER_WEIGHT: float = 1
    SPARSE_RETRIEVER_WEIGHT: float = 0

    RAG_TOP_K: int = 20
    RAG_TOP_N: int = 5

    RERANKER_MODEL: str = "accounts/fireworks/models/qwen3-reranker-8b"

    AGENT_NEEDS_RAG_MODEL: str = "accounts/fireworks/models/gpt-oss-20b"
    AGENT_QUERY_GENERATOR_MODEL: str = "accounts/fireworks/models/gpt-oss-20b"
    AGENT_QUERY_GENERATION_NUMBER: int = 4
    AGENT_TOP_K: int = 5
    AGENT_RETRIEVAL_EVALUATOR_MODEL: str = "accounts/fireworks/models/deepseek-v4-flash-0731"
    AGENT_GENERATOR_MODEL: str = "accounts/fireworks/models/kimi-k3"
    ENVIRONMENT: str = "development"
    VERSION: str = "1.0.0"
    REDIS_PORT: int = 6379
    REDIS_HOST: str = "redis"
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )



@lru_cache()
def get_settings():
    return Settings()