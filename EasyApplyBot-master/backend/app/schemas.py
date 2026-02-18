from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class FilterPayload(BaseModel):
    positions: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    remote_only: bool = False
    easy_apply_only: bool = True
    posted_within_hours: int = 24
    max_jobs_per_run: int = 20


class JobStatus(BaseModel):
    id: int
    title: str
    company: str
    location: str
    status: Literal['queued', 'processing', 'applied', 'skipped', 'failed']
    applied_at: datetime
    notes: str


class DashboardStats(BaseModel):
    total_applied: int
    applied_today: int
    failed_today: int
    skipped_today: int
    date: date


class RuntimeSettingsUpdate(BaseModel):
    linkedin_email: str | None = None
    linkedin_password: str | None = None
    openai_api_key: str | None = None
    openai_model: str | None = None


class RuntimeSettingsResponse(BaseModel):
    linkedin_email: str
    linkedin_password: str
    openai_api_key: str
    openai_model: str
    database_url: str
