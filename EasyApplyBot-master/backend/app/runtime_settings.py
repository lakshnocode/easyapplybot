from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from pydantic import BaseModel, Field

from .config import BASE_DIR, settings

STORE_PATH = BASE_DIR / 'runtime_settings.json'


class RuntimeSettings(BaseModel):
    linkedin_email: str = ''
    linkedin_password: str = ''
    openai_api_key: str = ''
    openai_model: str = 'gpt-4o-mini'
    database_url: str = 'sqlite:///./state.db'


class RuntimeSettingsStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._settings = RuntimeSettings(
            linkedin_email=settings.linkedin_email,
            linkedin_password=settings.linkedin_password,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            database_url=settings.database_url,
        )
        self._load_file()

    def _load_file(self) -> None:
        if not STORE_PATH.exists():
            return
        try:
            data = json.loads(STORE_PATH.read_text(encoding='utf-8'))
            self._settings = RuntimeSettings.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            return

    def _save_file(self) -> None:
        STORE_PATH.write_text(self._settings.model_dump_json(indent=2), encoding='utf-8')

    def get(self) -> RuntimeSettings:
        return self._settings

    def get_safe(self) -> RuntimeSettings:
        s = self._settings.model_copy(deep=True)
        s.linkedin_password = '********' if s.linkedin_password else ''
        s.openai_api_key = '********' if s.openai_api_key else ''
        return s

    def update(self, payload: dict) -> RuntimeSettings:
        with self._lock:
            current = self._settings.model_dump()
            for key, value in payload.items():
                if value is None:
                    continue
                if isinstance(value, str):
                    current[key] = value.strip()
                else:
                    current[key] = value
            self._settings = RuntimeSettings.model_validate(current)
            self._save_file()
            return self._settings


runtime_settings_store = RuntimeSettingsStore()
