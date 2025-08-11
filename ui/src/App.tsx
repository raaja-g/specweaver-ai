import React, { useState } from 'react';
import axios from 'axios';

export default function App() {
  const [story, setStory] = useState('');
  const [session, setSession] = useState<string | null>(null);
  const [tests, setTests] = useState<any[]>([]);
  const [uiMode, setUiMode] = useState<'real' | 'mock'>('real');
  const [apiMode, setApiMode] = useState<'mock' | 'stub' | 'real'>('mock');

  const upload = async () => {
    const res = await axios.post('http://localhost:8080/api/requirements', { story_text: story });
    setSession(res.data.session_id);
  };

  const generate = async () => {
    if (!session) return;
    const res = await axios.post(`http://localhost:8080/api/requirements/${session}/generate`, { coverage: 'comprehensive' });
    setTests(res.data.test_cases);
  };

  const approve = async () => {
    if (!session) return;
    const ids = tests.map(t => t.id);
    await axios.post(`http://localhost:8080/api/requirements/${session}/approve`, { test_case_ids: ids, approved: true });
  };

  const run = async () => {
    if (!session) return;
    await axios.post('http://localhost:8080/api/runs', { session_id: session, ui_mode: uiMode, api_mode: apiMode });
  };

  return (
    <div style={{ padding: 24 }}>
      <h1>SpecWeaver</h1>
      <textarea rows={8} cols={80} placeholder="Paste user story..." value={story} onChange={e => setStory(e.target.value)} />
      <div>
        <button onClick={upload}>1) Upload & Parse</button>
        <button onClick={generate} disabled={!session}>2) Generate Tests</button>
        <button onClick={approve} disabled={!tests.length}>3) Approve</button>
      </div>
      <div style={{ marginTop: 12 }}>
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
        <button style={{ marginLeft: 12 }} onClick={run} disabled={!session}>4) Run</button>
      </div>
      <h3>Generated Tests</h3>
      <ul>
        {tests.map(t => <li key={t.id}>{t.id} - {t.title} ({t.type})</li>)}
      </ul>
    </div>
  );
}
