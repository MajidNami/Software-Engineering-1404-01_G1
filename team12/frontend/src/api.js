// در حالت dev با پروکسی Vite از آدرس نسبی استفاده می‌کنیم تا به بک‌اند برسد
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : 'http://localhost:8000') + '/api';

export async function request(path, options = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.message || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getTests: () => request('/tests/'),
  startSession: (testId, mode) =>
    request('/sessions/start/', {
      method: 'POST',
      body: JSON.stringify({ test_id: testId, mode }),
    }),
  getSession: (sessionId) => request(`/sessions/${sessionId}/`),
  submitAnswer: (sessionId, questionId, optionId, responseTimeMs) =>
    request(`/sessions/${sessionId}/answers/`, {
      method: 'POST',
      body: JSON.stringify({
        question_id: questionId,
        option_id: optionId,
        ...(responseTimeMs != null && { response_time_ms: responseTimeMs }),
      }),
    }),
  finishSession: (sessionId) =>
    request(`/sessions/${sessionId}/finish/`, { method: 'POST' }),
  getScoreReport: (sessionId) => request(`/sessions/${sessionId}/score-report/`),
  logEvent: (sessionId, eventType, count = 1, extraData = {}) =>
    request(`/sessions/${sessionId}/events/`, {
      method: 'POST',
      body: JSON.stringify({ event_type: eventType, count, extra_data: extraData }),
    }),
  getItem: (itemId) => request(`/items/${itemId}/`),
};
