from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN", min_length=10)
    webhook_url: str = Field(alias="WEBHOOK_URL", min_length=5)
    webhook_path: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    max_message_len: int = Field(default=3500, alias="MAX_MESSAGE_LEN", ge=200, le=4000)
    rate_limit_calls: int = Field(default=10, alias="RATE_LIMIT_CALLS", ge=1, le=1000)
    rate_limit_window_sec: int = Field(default=30, alias="RATE_LIMIT_WINDOW_SEC", ge=1, le=3600)
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def webhook_full_url(self) -> str:
        return f"{self.webhook_url.rstrip('/')}{self.webhook_path}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
