"""App settings, loaded from environment variables or backend/.env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/taskmanager"
    nager_date_base_url: str = "https://date.nager.at/api/v3"
    default_country_code: str = "US"


settings = Settings()
