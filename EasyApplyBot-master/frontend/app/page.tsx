'use client';

import { useEffect, useState } from 'react';
import { getDashboard, getJobs, getSettings, saveSettings, startRun } from '../lib/api';

type Dashboard = { total_applied: number; applied_today: number; failed_today: number; skipped_today: number; date: string };
type Job = { id: number; title: string; company: string; location: string; status: string; notes: string; applied_at: string };

type RuntimeSettings = {
  linkedin_email: string;
  linkedin_password: string;
  openai_api_key: string;
  openai_model: string;
  database_url: string;
};

export default function HomePage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [positions, setPositions] = useState('Software Engineer,Backend Engineer');
  const [locations, setLocations] = useState('United States,Remote');
  const [remoteOnly, setRemoteOnly] = useState(true);
  const [settingsStatus, setSettingsStatus] = useState('');

  const [linkedinEmail, setLinkedinEmail] = useState('');
  const [linkedinPassword, setLinkedinPassword] = useState('');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [openaiModel, setOpenaiModel] = useState('gpt-4o-mini');

  async function refresh() {
    const [db, jobsData, runtime] = await Promise.all([getDashboard(), getJobs(), getSettings() as Promise<RuntimeSettings>]);
    setDashboard(db);
    setJobs(jobsData);
    setLinkedinEmail(runtime.linkedin_email || '');
    setOpenaiModel(runtime.openai_model || 'gpt-4o-mini');
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 15000);
    return () => clearInterval(id);
  }, []);

  async function persistSettings() {
    await saveSettings({
      linkedin_email: linkedinEmail,
      linkedin_password: linkedinPassword,
      openai_api_key: openaiApiKey,
      openai_model: openaiModel,
    });
    setLinkedinPassword('');
    setOpenaiApiKey('');
    setSettingsStatus('Settings saved. Secrets are now stored server-side.');
    await refresh();
  }

  async function runBot() {
    await startRun({
      positions: positions.split(',').map((x) => x.trim()).filter(Boolean),
      locations: locations.split(',').map((x) => x.trim()).filter(Boolean),
      remote_only: remoteOnly,
      easy_apply_only: true,
      posted_within_hours: 24,
      max_jobs_per_run: 20,
      keywords: []
    });
    await refresh();
  }

  return (
    <main className="container">
      <h1>EasyApply AI Dashboard</h1>
      <section className="cards">
        <article><h3>Total Applied</h3><p>{dashboard?.total_applied ?? 0}</p></article>
        <article><h3>Applied Today</h3><p>{dashboard?.applied_today ?? 0}</p></article>
        <article><h3>Failed Today</h3><p>{dashboard?.failed_today ?? 0}</p></article>
        <article><h3>Skipped Today</h3><p>{dashboard?.skipped_today ?? 0}</p></article>
      </section>

      <section className="panel">
        <h2>Account & AI Settings</h2>
        <label>LinkedIn email</label>
        <input value={linkedinEmail} onChange={(e) => setLinkedinEmail(e.target.value)} placeholder="you@example.com" />
        <label>LinkedIn password</label>
        <input type="password" value={linkedinPassword} onChange={(e) => setLinkedinPassword(e.target.value)} placeholder="Enter to update" />
        <label>OpenAI API key</label>
        <input type="password" value={openaiApiKey} onChange={(e) => setOpenaiApiKey(e.target.value)} placeholder="sk-... (optional)" />
        <label>OpenAI model</label>
        <input value={openaiModel} onChange={(e) => setOpenaiModel(e.target.value)} placeholder="gpt-4o-mini" />
        <button onClick={persistSettings}>Save settings</button>
        {settingsStatus ? <p className="ok">{settingsStatus}</p> : null}
      </section>

      <section className="panel">
        <h2>Filters</h2>
        <label>Positions</label>
        <input value={positions} onChange={(e) => setPositions(e.target.value)} />
        <label>Locations</label>
        <input value={locations} onChange={(e) => setLocations(e.target.value)} />
        <label className="inline">
          <input type="checkbox" checked={remoteOnly} onChange={(e) => setRemoteOnly(e.target.checked)} />
          Remote only
        </label>
        <button onClick={runBot}>Start applying</button>
      </section>

      <section>
        <h2>Recent Applications</h2>
        <table>
          <thead><tr><th>Role</th><th>Company</th><th>Status</th><th>Notes</th></tr></thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id}>
                <td>{job.title}</td>
                <td>{job.company}</td>
                <td>{job.status}</td>
                <td>{job.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
