const BASE = '/api';

async function req(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

export const api = {
  getPresentations: () => req('GET', '/presentations'),
  createSession: (presentation_file) => req('POST', '/sessions', { presentation_file }),
  getSession: (code) => req('GET', `/sessions/${code}`),
};
