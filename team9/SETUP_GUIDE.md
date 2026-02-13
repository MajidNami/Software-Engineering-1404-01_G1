# Team9 - Monolithic Architecture Setup

## Architecture Overview

### What Changed

The project has been refactored from **distributed** to **monolithic**:

**Before (Broken):**
```
Frontend (hardcoded localhost:8000) → Backend on separate container
- Fragile: localhost doesn't work in Docker
- 11 hardcoded URLs scattered across code
- No frontend service integration
- Gateway nginx config commented out
```

**After (Working):**
```
Windows/Docker:
frontend (Vite 5173) → nginx proxy (relative paths) → Vite dev proxy → Django (8000)

Docker:
frontend (built) → nginx gateway (9141) → Core Django (8000)
```

### Architecture: Monolithic Backend + Distributed Gateways

- **Core** (port 8000): Single Django app with all team APIs (Team1-Team15)
- **Team9 Gateway** (port 9141): Nginx reverse proxy that:
  - Serves built React frontend via nginx static files
  - Proxies API calls to Core
  - Runs independently via Docker
- **Result**: Frontend and Backend communicate through a single, reliable gateway

---

## How to Run

### Option 1: Windows Development (Recommended for Development)

```powershell
# Terminal 1: Start Django backend
cd C:\path\to\project
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Start Team9 frontend (Vite dev server)
cd team9/frontend
npm install  # First time only
npm run dev

# Visit: http://localhost:5173
```

**Why:** 
- Vite hot reloading works perfectly
- Vite proxy automatically routes `/team9/api/*` → `localhost:8000`
- No Docker overhead
- Instant feedback during development

### Option 2: Docker Full Stack (Production-like)

```powershell
# Navigate to project root
cd C:\path\to\project

# Run the main startup script
.\win_scripts\up-all.ps1

# OR run just core + Team9
.\win_scripts\up-team.ps1 -Team 9

# Visit: http://localhost:9141
```

**What happens:**
- Core starts on port 8000 (in Docker container)
- Team9 gateway starts on port 9141
  - Builds frontend from `team9/frontend/` 
  - Serves from nginx
  - Proxies API to core

**Stop all containers:**
```powershell
.\win_scripts\down-all.ps1
```

---

## Key Changes Made

### 1. Frontend API Configuration (`team9/frontend/src/config.js`)
**Before:** 11 hardcoded `http://127.0.0.1:8000` URLs scattered everywhere
**After:** Centralized relative paths

```javascript
export default {
  LESSONS_ENDPOINT: '/team9/api/lessons/',
  WORDS_ENDPOINT: '/team9/api/words/',
};
```

### 2. All JSX Files Updated
- `AddWord.jsx`
- `LessonDetail.jsx`
- `Microservices.jsx`
- `ReviewLesson.jsx`

Changed from:
```javascript
fetch("http://127.0.0.1:8000/team9/api/lessons/")
```

To:
```javascript
import config from '../config';
fetch(config.LESSONS_ENDPOINT)
```

### 3. Vite Dev Server Proxy (`team9/frontend/vite.config.js`)
```javascript
server: {
  proxy: {
    '/team9/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

This allows the frontend dev server to transparently route API calls to Django.

### 4. Team9 Docker Setup

**Dockerfile:**
- Builds React frontend (`npm run build`)
- Uses nginx to serve built files + proxy API requests

**docker-compose.yml:**
```yaml
services:
  gateway:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${TEAM_PORT}:80"  # 9141 for team9
    depends_on:
      - core
```

**gateway.conf (nginx):**
- Serves frontend static files from `/usr/share/nginx/html`
- Proxies `/team9/api/*` → `core:8000`
- Uses SPA routing (deep links → index.html)

---

## Troubleshooting

### Problem: "Cannot GET /team9/api/lessons" (404 in Docker)

**Cause:** nginx gateway can't reach core service

**Solution:**
```bash
# Check if core is running
docker ps | grep app404_core  # Should be running

# If core crashed, restart all
.\win_scripts\down-all.ps1
.\win_scripts\up-all.ps1
```

### Problem: "Failed to fetch" in browser (Development)

**Cause:** Vite proxy not working or Django not running

**Check:**
```powershell
# 1. Is Vite running on 5173?
netstat -ano | findstr :5173

# 2. Is Django running on 8000?
netstat -ano | findstr :8000

# 3. Check Vite logs for proxy errors
# Terminal with Vite should show details
```

### Problem: CORS errors in Docker

**Cause:** Django CORS not configured correctly

**Check:** [app404/settings.py](../app404/settings.py)
- DEBUG mode allows `localhost:*` automatically ✓
- In production, must set `CORS_ALLOWED_ORIGINS`

### Problem: Frontend shows blank page

**Cause:** SPA routing or static files not served correctly

**Check:**
```bash
# Log into gateway container
docker exec -it <gateway-container> sh

# List files
ls -la /usr/share/nginx/html/team9/
# Should see: index.html, assets/, etc.

# Test proxy
curl http://localhost/team9/api/lessons/
```

---

## Development Workflow

### Working with Frontend

```powershell
cd team9/frontend
npm run dev
# Edit React files → auto-refresh at localhost:5173
```

### Working with Backend

```powershell
python manage.py runserver
# Edit Django files → auto-reload on save
# API automatically available to frontend via proxy
```

### Making API Changes

1. Edit `/team9/models.py` or `/team9/views.py`
2. Django auto-reloads
3. Frontend automatically calls new endpoints (same relative paths)
4. No frontend changes needed!

---

## Architecture Decisions

### Why Monolithic Backend?

| Aspect | Distributed | Monolithic ✓ |
|--------|-------------|-------------|
| **Complexity** | 16 Docker services | 1 core + proxies |
| **Single point of failure** | Team9 breaks = team9 down | Core breaks = all teams down |
| **Development** | Docker overhead | Native Python, fast |
| **Team coordination** | Each team owns their API | Core team manages APIs |
| **This project** | 15 teams, most incomplete | 1 real team (Team9) with full frontend |

**Verdict:** Monolithic is the right call for an academic project where teams share an app.

### Why Nginx Gateway?

Instead of serving frontend from Django:
- Lightweight reverse proxy (nginx is tiny)
- Separates concerns: static files vs. API
- Scales better (can load balance later)
- Docker-friendly (standard pattern)

---

## File Map

```
project/
├── win_scripts/          # DO NOT MODIFY - required by setup
│   ├── up-all.ps1
│   ├── up-team.ps1
│   └── down-all.ps1
│
├── app404/               # Django config (monolithic core)
│   └── settings.py       # CORS allows localhost:*
│
├── team9/                # Team9 app
│   ├── Dockerfile        # NEW: Builds frontend + sets up nginx
│   ├── docker-compose.yml # UPDATED: Enables Team9 gateway
│   ├── gateway.conf      # UPDATED: Routes frontend + proxies API
│   ├── views.py          # Unchanged - provides REST API
│   ├── models.py         # Unchanged - data models
│   │
│   └── frontend/         # React app
│       ├── vite.config.js    # UPDATED: Added proxy config
│       ├── src/config.js     # NEW: API endpoint config
│       └── src/pages/*.jsx   # UPDATED: Use config instead of hardcoded URLs
│           ├── AddWord.jsx
│           ├── LessonDetail.jsx
│           ├── Microservices.jsx
│           └── ReviewLesson.jsx
```

---

## Next Steps

### For you (now):
- [ ] Test with `npm run dev` (Windows dev mode)
- [ ] Test with `.\win_scripts\up-team.ps1 -Team 9` (Docker mode)
- [ ] Verify both work correctly

### For other teams (future):
- Each team's docker-compose can follow same pattern
- Or keep with current setup (doesn't matter, core handles everything)

---

## Questions?

Check:
1. Is Django running? (`netstat -ano | findstr :8000`)
2. Is frontend running? (`netstat -ano | findstr :5173` or `:9141` in Docker)
3. Are docker containers running? (`docker ps`)
4. Check console logs for errors (both browser DevTools + terminal)
