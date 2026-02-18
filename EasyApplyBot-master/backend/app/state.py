from datetime import date, datetime

from sqlmodel import Session, SQLModel, create_engine, select

from .config import settings
from .models import JobApplication


engine = create_engine(settings.database_url, connect_args={'check_same_thread': False} if settings.database_url.startswith('sqlite') else {})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def upsert_job(job_id: str, title: str, company: str, location: str, status: str, notes: str = '') -> JobApplication:
    with Session(engine) as session:
        statement = select(JobApplication).where(JobApplication.job_id == job_id)
        job = session.exec(statement).first()
        if not job:
            job = JobApplication(job_id=job_id, title=title, company=company, location=location, status=status, notes=notes)
        else:
            job.title = title
            job.company = company
            job.location = location
            job.status = status
            if notes:
                job.notes = notes
        session.add(job)
        session.commit()
        session.refresh(job)
        return job


def list_jobs(limit: int = 100) -> list[JobApplication]:
    with Session(engine) as session:
        statement = select(JobApplication).order_by(JobApplication.applied_at.desc()).limit(limit)
        return list(session.exec(statement).all())


def dashboard_stats() -> dict:
    today = date.today()
    with Session(engine) as session:
        rows = list(session.exec(select(JobApplication)).all())

    total_applied = sum(1 for j in rows if j.status == 'applied')
    applied_today = sum(1 for j in rows if j.status == 'applied' and j.applied_at.date() == today)
    failed_today = sum(1 for j in rows if j.status == 'failed' and j.applied_at.date() == today)
    skipped_today = sum(1 for j in rows if j.status == 'skipped' and j.applied_at.date() == today)

    return {
        'total_applied': total_applied,
        'applied_today': applied_today,
        'failed_today': failed_today,
        'skipped_today': skipped_today,
        'date': datetime.utcnow().date(),
    }
