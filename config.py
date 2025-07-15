from typing import List, Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests.auth import HTTPBasicAuth

class Config(BaseSettings):
    """Configuration class for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment settings
    llm_model_name: str = "gpt-4.1-mini"
    openai_api_key: str
    upload_dir: str = "uploads"

    # Memory
    memory_length: int = 5
    message_log_directory: str = "temp/message_logs"
    upload_dir: str = "temp/uploads"

    # Application settings
    fastapi_keys: list[str]
    auth_encryption_key: str

configs = Config()