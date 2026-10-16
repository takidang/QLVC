from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env nằm ở thư mục gốc repo (cạnh docker-compose.yml)
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    # Không có giá trị mặc định cho bí mật: thiếu thì không khởi động (security-rules.md)
    database_url: str
    jwt_secret: str = Field(min_length=32)
    app_env: Literal["dev", "demo"] = "dev"
    luu_tru: Literal["local", "supabase"] = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
