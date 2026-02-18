'use client';

import { useEffect, useState } from 'react';
import { getDashboard, getJobs, startRun } from '../lib/api';

type Dashboard = { total_applied: number; applied_today: number; failed_today: number; skipped_today: number; date: string };
type Job = { id: number; title: string; company: string; location: string; status: string; notes: string; applied_at: string };

export default function HomePage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [positions, setPositions] = useState('Software Engineer,Backend Engineer');
  const [locations, setLocations] = useState('United States,Remote');
  const [remoteOnly, setRemoteOnly] = useState(true);

  async function refresh() {
    const [db, jobsData] = await Promise.all([getDashboard(), getJobs()]);
    setDashboard(db);
    setJobs(jobsData);
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 15000);
    return () => clearInterval(id);
  }, []);

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
