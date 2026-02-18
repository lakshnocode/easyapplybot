from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class JobApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    title: str
    company: str
    location: str
    status: str = Field(default='queued', index=True)
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str = ''


class RunConfig(SQLModel):
    positions: list[str]
    locations: list[str]
    keywords: list[str] = []
    remote_only: bool = False
    skip_seen: bool = True
    max_jobs_per_run: int = 20
