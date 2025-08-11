import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { Bar, Line } from 'react-chartjs-2';
import hljs from 'highlight.js/lib/core';
import diffLang from 'highlight.js/lib/languages/diff';
import 'highlight.js/styles/atom-one-dark.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

type TestCaseSummary = { id: string; title: string; type: string; priority: string; trace_to: string[] };
type Duplicate = { file: string; reason: string };

export default function App() {
  const [story, setStory] = useState('');
  const [session, setSession] = useState<string | null>(null);
  const [tests, setTests] = useState<TestCaseSummary[]>([]);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [duplicates, setDuplicates] = useState<Duplicate[]>([]);
  const [uiMode, setUiMode] = useState<'real' | 'mock'>('real');
  const [apiMode, setApiMode] = useState<'mock' | 'stub' | 'real'>('mock');
  const [autoPR, setAutoPR] = useState<boolean>(false);
  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [allowDup, setAllowDup] = useState<boolean>(false);
  const [diffs, setDiffs] = useState<any[] | null>(null);
  const [showDiffs, setShowDiffs] = useState<boolean>(false);

  useEffect(() => {
    hljs.registerLanguage('diff', diffLang);
  }, []);

  const api = 'http://localhost:8080';

  const upload = async () => {
    const res = await axios.post(`${api}/api/requirements`, { story_text: story });
    setSession(res.data.session_id);
  };

  const generate = async () => {
    if (!session) return;
    try {
      const res = await axios.post(`${api}/api/requirements/${session}/generate`, {
        coverage: 'comprehensive',
        allow_duplicates: allowDup,
      });
      setTests(res.data.test_cases);
      setDuplicates(res.data.duplicates || []);
      setSelected(Object.fromEntries(res.data.test_cases.map((t: TestCaseSummary) => [t.id, true])));
    } catch (e: any) {
      if (e.response?.status === 409) {
        setDuplicates(e.response.data.detail?.duplicates || []);
        alert('Duplicate tests found. Enable Allow duplicates or refine selection.');
      } else {
        alert('Generate failed');
      }
    }
  };

  const approve = async () => {
    if (!session) return;
    const ids = tests.filter(t => selected[t.id]).map(t => t.id);
    // Request preview diffs first
    try {
      const pv = await axios.post(`${api}/api/requirements/${session}/preview`, { test_case_ids: ids });
      setDiffs(pv.data.diffs || []);
      setShowDiffs(true);
      return;
    } catch (e) {
      // fallback to immediate approve if preview not available
    }
    try {
      await axios.post(`${api}/api/requirements/${session}/approve`, {
        test_case_ids: ids,
        approved: true,
        allow_duplicates: allowDup,
      });
      alert('Approved and generated tests.');
    } catch (e: any) {
      if (e.response?.status === 409) {
        setDuplicates(e.response.data.detail?.duplicates || []);
        alert('Duplicate tests found. Enable Allow duplicates or change selection.');
      } else {
        alert('Approve failed');
      }
    }
  };

  const confirmApprove = async () => {
    if (!session) return;
    const ids = tests.filter(t => selected[t.id]).map(t => t.id);
    try {
      await axios.post(`${api}/api/requirements/${session}/approve`, {
        test_case_ids: ids,
        approved: true,
        allow_duplicates: allowDup,
      });
      setShowDiffs(false);
      alert('Approved and generated tests.');
    } catch (e: any) {
      if (e.response?.status === 409) {
        setDuplicates(e.response.data.detail?.duplicates || []);
        alert('Duplicate tests found. Enable Allow duplicates or change selection.');
      } else {
        alert('Approve failed');
      }
    }
  };

  const run = async () => {
    if (!session) return;
    const res = await axios.post(`${api}/api/runs`, {
      session_id: session,
      ui_mode: uiMode,
      api_mode: apiMode,
      auto_pr: autoPR,
    });
    setRunId(res.data.run_id);
    setRunStatus({ status: 'queued' });
  };

  // Poll run status
  useEffect(() => {
    if (!runId) return;
    const interval = setInterval(async () => {
      try {
        // Ask API to refresh from artifacts if worker is used
        await axios.post(`${api}/api/runs/${runId}/refresh`);
        const res = await axios.get(`${api}/api/runs/${runId}`);
        setRunStatus(res.data);
        if (["completed", "failed", "error"].includes(res.data.status)) {
          clearInterval(interval);
        }
      } catch {
        // ignore
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [runId]);

  // Fetch dashboard metrics
  const fetchMetrics = async () => {
    const res = await axios.get(`${api}/api/metrics`);
    setMetrics(res.data);
  };
  useEffect(() => { fetchMetrics(); }, [runStatus?.status]);

  const chartData = useMemo(() => {
    if (!metrics) return { labels: [], datasets: [] };
    const labels = Object.keys(metrics.test_types || {});
    const data = Object.values(metrics.test_types || {});
    return {
      labels,
      datasets: [
        {
          label: 'Test Types Count',
          backgroundColor: 'rgba(99, 102, 241, 0.6)',
          data,
        },
      ],
    };
  }, [metrics]);

  const timeSeries = useMemo(() => {
    if (!metrics?.history) return { labels: [], datasets: [] };
    const labels = metrics.history.map((m: any) => (m.completed_at || m.created_at || '').slice(11, 19));
    const data = metrics.history.map((m: any) => (m.status === 'completed' ? 1 : 0));
    return {
      labels,
      datasets: [
        { label: 'Pass (1=yes)', data, borderColor: 'rgba(16,185,129,1)', backgroundColor: 'rgba(16,185,129,0.2)' },
      ],
    };
  }, [metrics]);

  return (
    <div style={{ padding: 24, fontFamily: 'Inter, system-ui, Arial' }}>
      <h1>SpecWeaver</h1>
      <div style={{ display: 'flex', gap: 16 }}>
        <div style={{ flex: 1 }}>
          <h3>Create Requirement</h3>
          <textarea rows={8} cols={80} placeholder="Paste user story..." value={story} onChange={e => setStory(e.target.value)} />
          <div style={{ marginTop: 8 }}>
            <button onClick={upload}>1) Upload & Parse</button>
            <label style={{ marginLeft: 12 }}>
              <input type="checkbox" checked={allowDup} onChange={e => setAllowDup(e.target.checked)} /> Allow duplicates
            </label>
            <button onClick={generate} disabled={!session} style={{ marginLeft: 12 }}>2) Generate Tests</button>
          </div>

          <h3 style={{ marginTop: 16 }}>HIL Review & Approval</h3>
          {duplicates.length > 0 && (
            <div style={{ color: '#b91c1c', marginBottom: 8 }}>
              Duplicates detected:
              <ul>
                {duplicates.map((d, i) => (
                  <li key={i}>{d.reason} in {d.file}</li>
                ))}
              </ul>
            </div>
          )}
          <div style={{ maxHeight: 240, overflow: 'auto', border: '1px solid #eee' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th align="left">Approve</th>
                  <th align="left">ID</th>
                  <th align="left">Title</th>
                  <th align="left">Type</th>
                  <th align="left">Priority</th>
                </tr>
              </thead>
              <tbody>
                {tests.map(t => (
                  <tr key={t.id}>
                    <td><input type="checkbox" checked={!!selected[t.id]} onChange={e => setSelected({ ...selected, [t.id]: e.target.checked })} /></td>
                    <td>{t.id}</td>
                    <td title={t.title}>{t.title}</td>
                    <td>{t.type}</td>
                    <td>{t.priority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button onClick={approve} disabled={!tests.length} style={{ marginTop: 8 }}>3) Approve Selected</button>

          {showDiffs && (
            <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ width: '80%', maxHeight: '80%', overflow: 'auto', background: 'white', padding: 16, borderRadius: 8 }}>
                <h3>Preview diffs</h3>
                {diffs?.length ? (
                  diffs.map((d, i) => (
                    <div key={i} style={{ marginBottom: 16 }}>
                      <div><b>{d.type}</b> {d.exists ? '(update)' : '(new)'} — {d.preview_path}</div>
                      <pre style={{ background: '#0f172a', color: '#e2e8f0', padding: 8, overflow: 'auto' }}>
                        <code className="language-diff" dangerouslySetInnerHTML={{ __html: hljs.highlight(d.diff || 'No existing file to diff', { language: 'diff' }).value }} />
                      </pre>
                    </div>
                  ))
                ) : (
                  <div>No diffs available</div>
                )}
                <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                  <button onClick={() => setShowDiffs(false)}>Cancel</button>
                  <button onClick={confirmApprove}>Confirm Approve</button>
                </div>
              </div>
            </div>
          )}

          <h3 style={{ marginTop: 16 }}>Run</h3>
          <div>
            <label>UI Mode: </label>
            <select value={uiMode} onChange={e => setUiMode(e.target.value as any)}>
              <option value="real">real</option>
              <option value="mock">mock</option>
            </select>
            <label style={{ marginLeft: 12 }}>API Mode: </label>
            <select value={apiMode} onChange={e => setApiMode(e.target.value as any)}>
              <option value="mock">mock</option>
              <option value="stub">stub</option>
              <option value="real">real</option>
            </select>
            <label style={{ marginLeft: 12 }}>
              <input type="checkbox" checked={autoPR} onChange={e => setAutoPR(e.target.checked)} /> Auto-PR on pass
            </label>
            <button style={{ marginLeft: 12 }} onClick={run} disabled={!session}>4) Run</button>
          </div>
          {runId && (
            <div style={{ marginTop: 8 }}>
              <div>Run ID: {runId}</div>
              <div>Status: {runStatus?.status}</div>
              {runStatus?.output && (
                <pre style={{ whiteSpace: 'pre-wrap', background: '#f8fafc', padding: 8, border: '1px solid #eee' }}>{runStatus.output}</pre>
              )}
            </div>
          )}
        </div>
        <div style={{ flex: 1 }}>
          <h3>Dashboard</h3>
          <div style={{ height: 300 }}>
            <Bar data={chartData as any} options={{ responsive: true, plugins: { legend: { display: false }, title: { display: true, text: 'Current Run Distribution' } } }} />
          </div>
          <div style={{ height: 240, marginTop: 12 }}>
            <Line data={timeSeries as any} options={{ responsive: true, plugins: { legend: { display: true }, title: { display: true, text: 'Pass Trend (recent runs)' } } }} />
          </div>
          <div style={{ marginTop: 8 }}>Pass rate: {metrics?.pass_rate?.toFixed?.(1) ?? 0}%</div>
        </div>
      </div>
    </div>
  );
}
