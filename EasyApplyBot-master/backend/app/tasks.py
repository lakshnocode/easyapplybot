from __future__ import annotations

import asyncio
import threading

from .ai_answerer import AIAnswerer
from .linkedin_bot import JobCard, LinkedinBot
from .state import upsert_job


class RunManager:
    def __init__(self) -> None:
        self._running = False
        self._lock = threading.Lock()

    @property
    def running(self) -> bool:
        return self._running

    def start(self, filters: dict) -> bool:
        with self._lock:
            if self._running:
                return False
            self._running = True

        thread = threading.Thread(target=self._run_worker, args=(filters,), daemon=True)
        thread.start()
        return True

    def _run_worker(self, filters: dict) -> None:
        try:
            asyncio.run(self._run(filters))
        finally:
            with self._lock:
                self._running = False

    async def _run(self, filters: dict) -> None:
        bot = LinkedinBot(AIAnswerer())

        async def on_job(status: str, job: JobCard, notes: str = ''):
            upsert_job(job_id=job.job_id, title=job.title, company=job.company, location=job.location, status=status, notes=notes)

        await bot.run(filters=filters, on_job=on_job)


run_manager = RunManager()
