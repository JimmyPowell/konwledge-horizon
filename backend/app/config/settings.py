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
    LLM_DEFAULT_MODEL: str = "Pro/deepseek-ai/DeepSeek-V3.1"
    LLM_MAX_TURNS: int = 12  # max turns to include in context window
    LLM_MAX_TOKENS: int = 1024  # default completion tokens cap
    LLM_API_BASE: str = "https://api.siliconflow.cn/v1"

    @property
    def mysql_database_url(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    # No need for model_config to specify env_file anymore, as we've loaded it manually
    model_config = SettingsConfigDict(env_file_encoding='utf-8')

settings = Settings()
