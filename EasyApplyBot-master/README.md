# EasyApply AI (LinkedIn automation + dashboard)

This refactor modernizes the project into two apps:

- `backend/` FastAPI + Playwright worker for LinkedIn Easy Apply automation.
- `frontend/` Next.js dashboard with filters, "applied today" metrics, and recent job statuses.

## Features

- Updated to current libraries (FastAPI, Playwright, Next.js 15, React 19).
- AI-backed application question answering (OpenAI API) with fallback heuristics.
- Handles text fields, dropdowns, and radio questions in Easy Apply forms.
- Skips long applications with a per-job timeout (`MAX_JOB_MINUTES`).
- Tracks `queued/processing/applied/skipped/failed` statuses in SQLite.
- Front-end includes filters and live-refreshing stats.

## Where to enter API key, LinkedIn email/password, and DB

You now enter LinkedIn/OpenAI credentials directly in the **frontend dashboard**:

- Open the app in the browser (`http://localhost:3000`)
- Use the **Account & AI Settings** panel
- Click **Save settings**

The backend stores these runtime values in `runtime_settings.json` at repo root, and uses them for automation.

Use `.env` only for infrastructure defaults (like `NEXT_PUBLIC_API_URL`/CORS/DB defaults), not for day-to-day credential input.

## Quick start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m playwright install chromium
uvicorn backend.app.main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Deploying

### Front-end on Vercel

Deploy `frontend/` to Vercel and set:

- `NEXT_PUBLIC_API_URL=https://<your-backend-domain>`

### Backend hosting (required for browser automation)

Playwright automation requires a long-running worker and headless browser support, so host `backend/` on Render, Railway, Fly.io, or a VM/container.

Set environment variables from `.env.example`.

## Notes

- This targets LinkedIn Easy Apply flows. External ATS forms vary widely; unsupported flows are skipped with a reason.
- Keep profile details truthful and compliant with platform terms.
