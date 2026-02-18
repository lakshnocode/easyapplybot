from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / '.env', BASE_DIR / 'backend' / '.env'),
        env_file_encoding='utf-8',
        extra='ignore',
    )

    app_name: str = 'EasyApply AI Orchestrator'
    database_url: str = Field(default='sqlite:///./state.db', alias='DATABASE_URL')
    linkedin_email: str = Field(default='', alias='LINKEDIN_EMAIL')
    linkedin_password: str = Field(default='', alias='LINKEDIN_PASSWORD')
    openai_api_key: str = Field(default='', alias='OPENAI_API_KEY')
    openai_model: str = Field(default='gpt-4o-mini', alias='OPENAI_MODEL')
    backend_public_url: str = Field(default='http://localhost:8000', alias='BACKEND_PUBLIC_URL')
    frontend_public_url: str = Field(default='http://localhost:3000', alias='FRONTEND_PUBLIC_URL')
    max_job_minutes: int = Field(default=5, alias='MAX_JOB_MINUTES')


settings = Settings()
