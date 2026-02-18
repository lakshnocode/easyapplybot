from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .runtime_settings import runtime_settings_store
from .schemas import (
    DashboardStats,
    FilterPayload,
    JobStatus,
    RuntimeSettingsResponse,
    RuntimeSettingsUpdate,
)
from .state import dashboard_stats, init_db, list_jobs
from .tasks import run_manager

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_public_url, 'http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def startup_event() -> None:
    init_db()


@app.get('/health')
def health() -> dict:
    return {'ok': True, 'running': run_manager.running}


@app.get('/api/settings', response_model=RuntimeSettingsResponse)
def get_settings():
    return runtime_settings_store.get_safe()


@app.post('/api/settings', response_model=RuntimeSettingsResponse)
def update_settings(payload: RuntimeSettingsUpdate):
    runtime_settings_store.update(payload.model_dump(exclude_unset=True))
    return runtime_settings_store.get_safe()


@app.get('/api/jobs', response_model=list[JobStatus])
def jobs(limit: int = 100):
    return list_jobs(limit=limit)


@app.get('/api/dashboard', response_model=DashboardStats)
def dashboard():
    return dashboard_stats()


@app.post('/api/run')
def start_run(filters: FilterPayload):
    current = runtime_settings_store.get()
    if not current.linkedin_email or not current.linkedin_password:
        raise HTTPException(status_code=400, detail='LinkedIn credentials are missing. Save them in dashboard settings first.')

    started = run_manager.start(filters.model_dump())
    if not started:
        raise HTTPException(status_code=409, detail='A run is already in progress.')
    return {'started': True}
