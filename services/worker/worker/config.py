from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    log_level: str = Field(default='INFO', alias='LOG_LEVEL')
    database_url: str = Field(alias='DATABASE_URL')
    redis_url: str = Field(alias='REDIS_URL')
    worker_concurrency: int = Field(default=1, alias='WORKER_CONCURRENCY')

    max_attempts: int = Field(default=3, alias='WORKER_MAX_ATTEMPTS')
    backoff_base_seconds: float = Field(default=1.0, alias='WORKER_BACKOFF_BASE_SECONDS')
    backoff_max_seconds: float = Field(default=30.0, alias='WORKER_BACKOFF_MAX_SECONDS')


settings = Settings()
