import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Build the path to the .env file
# This assumes settings.py is in backend/app/config/
# The .env file is in backend/
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # MySQL Configuration
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # JWT Configuration
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email Configuration
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_TLS: bool = True
    MAIL_SSL: bool = True

    # LLM / Chat settings
    SILICONFLOW_API_KEY: Optional[str] = None
    LLM_DEFAULT_MODEL: str = "moonshotai/Kimi-K2-Instruct-0905"
    LLM_MAX_TURNS: int = 12  # max turns to include in context window
    LLM_MAX_TOKENS: int = 1024  # default completion tokens cap
    LLM_API_BASE: str = "https://api.siliconflow.cn/v1"

    # File storage
    STORAGE_ROOT: str = "storage"
    MAX_UPLOAD_BYTES: int = 100 * 1024 * 1024

    # Chroma vector DB (independent server recommended)
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_PATH: str = "./chroma_data"  # used only for embedded mode

    # Embedding / indexing defaults
    EMBEDDING_MODEL_DEFAULT: str = "Qwen/Qwen3-Embedding-8B"
    CHUNK_SIZE_DEFAULT: int = 1000
    CHUNK_OVERLAP_DEFAULT: int = 200
    PARSE_STRATEGY_DEFAULT: str = "auto"

    # Retrieval / RAG settings
    RAG_ENABLED: bool = True
    RAG_TOP_K: int = 6
    RAG_PER_KB_K: int | None = None
    RERANK_ENABLED: bool = False
    RERANK_MODEL: str = "Qwen/Qwen3-Reranker-8B"
    RERANK_TOP_N: int = 6
    MAX_CONTEXT_CHARS: int = 8000

    # Title generation
    LLM_TITLE_MODEL: Optional[str] = None  # fallback to LLM_DEFAULT_MODEL if None
    TITLE_MAX_TOKENS: int = 32
    TITLE_MAX_LENGTH_CHARS: int = 40

    # PDF parsing / OCR fallback (disabled/removed by default)

    @property
    def mysql_database_url(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    # No need for model_config to specify env_file anymore, as we've loaded it manually
    model_config = SettingsConfigDict(env_file_encoding='utf-8')

settings = Settings()
