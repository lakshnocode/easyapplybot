const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getDashboard() {
  const res = await fetch(`${API_BASE}/api/dashboard`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch dashboard');
  return res.json();
}

export async function getJobs() {
  const res = await fetch(`${API_BASE}/api/jobs`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return res.json();
}

export async function getSettings() {
  const res = await fetch(`${API_BASE}/api/settings`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function saveSettings(payload: unknown) {
  const res = await fetch(`${API_BASE}/api/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function startRun(filters: unknown) {
  const res = await fetch(`${API_BASE}/api/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters),
  });
  if (!res.ok) throw new Error(await res.text());
}
