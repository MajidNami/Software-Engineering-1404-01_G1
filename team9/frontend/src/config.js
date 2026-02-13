// API Configuration
// Works with both development (Vite proxy) and Docker (relative paths via nginx)

// In development: Vite proxy is configured to forward /team9/api to localhost:8000
// In Docker: nginx gateway proxies /team9/api to core:8000
// Both use relative paths, so they work transparently

const API_BASE_URL = '';

export default {
  API_BASE_URL,
  LESSONS_ENDPOINT: '/team9/api/lessons/',
  WORDS_ENDPOINT: '/team9/api/words/',
  DASHBOARD_ENDPOINT: '/team9/api/dashboard/',
};
