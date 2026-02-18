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

## Next steps to run this LinkedIn bot

### 1) Start backend

From repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m playwright install chromium
cp .env.example .env
uvicorn backend.app.main:app --reload --port 8000
```

### 2) Start frontend dashboard

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

### 3) Save credentials from dashboard

In **Account & AI Settings**:

- LinkedIn email
- LinkedIn password
- OpenAI API key (optional but recommended)
- OpenAI model (default `gpt-4o-mini`)

Click **Save settings**.

### 4) Configure filters and start applying

In **Filters**:

- Enter comma-separated positions
- Enter comma-separated locations
- Toggle remote-only if needed
- Click **Start applying**

### 5) Monitor results

- Top cards show totals/applied/failed/skipped
- Recent Applications table shows job-level statuses and notes
- Dashboard auto-refreshes every ~15 seconds

### 6) Optional backend API checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/settings
curl http://localhost:8000/api/dashboard
```

### 7) Common issues

- `POST /api/run` returns 400: LinkedIn credentials were not saved from dashboard settings.
- Browser errors: run `python -m playwright install chromium` again.
- Frontend dependency install fails (`npm` registry/proxy issue): fix network/proxy policy and rerun `npm install`.

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
