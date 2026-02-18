from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright

from .ai_answerer import AIAnswerer
from .config import settings
from .runtime_settings import runtime_settings_store


@dataclass
class JobCard:
    job_id: str
    title: str
    company: str
    location: str


class LinkedinBot:
    def __init__(self, answerer: AIAnswerer) -> None:
        self.answerer = answerer

    async def run(self, filters: dict, on_job) -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await self._login(page)
            await self._open_job_search(page, filters)

            jobs = await self._collect_jobs(page, filters.get('max_jobs_per_run', 20))
            for job in jobs:
                await on_job('processing', job)
                ok, note = await self._apply_to_job(page, job)
                await on_job('applied' if ok else 'skipped', job, note)

            await context.close()
            await browser.close()

    async def _login(self, page):
        await page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
        runtime_settings = runtime_settings_store.get()
        if not runtime_settings.linkedin_email or not runtime_settings.linkedin_password:
            raise RuntimeError('Missing LinkedIn credentials. Save them from the dashboard Settings panel.')
        await page.fill('#username', runtime_settings.linkedin_email)
        await page.fill('#password', runtime_settings.linkedin_password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')

    async def _open_job_search(self, page, filters: dict):
        query = '+'.join(filters.get('positions', ['Software Engineer']))
        location = '+'.join(filters.get('locations', ['United States']))
        remote = '&f_WT=2' if filters.get('remote_only') else ''
        easy_apply = '&f_AL=true' if filters.get('easy_apply_only', True) else ''
        await page.goto(
            f'https://www.linkedin.com/jobs/search/?keywords={query}&location={location}{remote}{easy_apply}',
            wait_until='domcontentloaded',
        )
        await page.wait_for_timeout(1500)

    async def _collect_jobs(self, page, limit: int) -> list[JobCard]:
        cards = page.locator('li.jobs-search-results__list-item')
        count = await cards.count()
        jobs: list[JobCard] = []
        for idx in range(min(count, limit)):
            card = cards.nth(idx)
            link = card.locator('a.job-card-container__link')
            href = await link.get_attribute('href') or ''
            job_id = href.split('currentJobId=')[-1].split('&')[0] if 'currentJobId=' in href else str(idx)
            jobs.append(
                JobCard(
                    job_id=job_id,
                    title=(await card.locator('strong').inner_text()).strip(),
                    company=(await card.locator('.artdeco-entity-lockup__subtitle').inner_text()).strip(),
                    location=(await card.locator('.job-card-container__metadata-item').inner_text()).strip(),
                )
            )
        return jobs

    async def _apply_to_job(self, page, job: JobCard) -> tuple[bool, str]:
        start = time.monotonic()
        try:
            await page.goto(f'https://www.linkedin.com/jobs/view/{job.job_id}', wait_until='domcontentloaded')
            await page.click('button.jobs-apply-button', timeout=3000)
        except PlaywrightTimeout:
            return False, 'No Easy Apply button found'

        while True:
            if time.monotonic() - start > settings.max_job_minutes * 60:
                close = page.locator('button[aria-label="Dismiss"]')
                if await close.count():
                    await close.first.click()
                return False, 'Skipped due to max-job timeout'

            await self._answer_visible_questions(page)

            submit = page.locator('button[aria-label="Submit application"]')
            if await submit.count() and await submit.first.is_enabled():
                await submit.first.click()
                await asyncio.sleep(1)
                return True, 'Submitted'

            next_btn = page.locator('button[aria-label="Continue to next step"], button[aria-label="Review your application"]')
            if await next_btn.count() and await next_btn.first.is_enabled():
                await next_btn.first.click()
                await asyncio.sleep(0.8)
                continue

            return False, 'Could not continue application flow'

    async def _answer_visible_questions(self, page) -> None:
        text_inputs = page.locator('input[type="text"], input[type="number"], textarea')
        input_count = await text_inputs.count()
        for i in range(input_count):
            el = text_inputs.nth(i)
            value = await el.input_value()
            if value:
                continue
            label_id = await el.get_attribute('id')
            label_text = label_id or 'Application question'
            answer = await self.answerer.answer(label_text)
            await el.fill(answer)

        selects = page.locator('select')
        select_count = await selects.count()
        for i in range(select_count):
            sel = selects.nth(i)
            options = [o.strip() for o in await sel.locator('option').all_inner_texts() if o.strip()]
            answer = await self.answerer.answer('Select best matching option', options=options)
            try:
                await sel.select_option(label=answer)
            except PlaywrightTimeout:
                if options:
                    await sel.select_option(index=1 if len(options) > 1 else 0)

        radios = page.locator('input[type="radio"]')
        radio_count = await radios.count()
        for i in range(radio_count):
            radio = radios.nth(i)
            checked = await radio.is_checked()
            if not checked:
                await radio.check()
                break
