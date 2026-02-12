# TOEFL Listening Test & Practice

Backend: Django + DRF + JWT. Frontend: React + Vite + Tailwind. UI design reference: [Figma](https://www.figma.com/design/Rdhjj0chLF6YbtOIMSd7EA/Listening_Figma).

## Backend (Django)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py load_sample_data   # 5 tests, 6 items, 10 questions (optional)
python manage.py createsuperuser   # optional, for admin
python manage.py runserver
```

برای پر کردن دیتابیس با دادهٔ نمونه (بدون ورود دستی):
```bash
python manage.py load_sample_data        # فقط اگر هیچ تستی نداری
python manage.py load_sample_data --clear   # پاک کردن تست‌های قبلی و لود مجدد
```

API base: `http://localhost:8000/api`. JWT: `POST /api/auth/token/` with `username`, `password`.

## Frontend (React)

ابتدا بک‌اند را اجرا کنید، بعد فرانت را:

```bash
cd frontend
npm install
npm run dev
```

در حالت dev، Vite درخواست‌های `/api` و `/media` را به `http://127.0.0.1:8000` پروکسی می‌کند؛ نیازی به تنظیم CORS یا آدرس دستی نیست.

## Docker

```bash
docker compose up --build
```

| Service   | URL                      | Port (host → container) |
|-----------|--------------------------|--------------------------|
| **Backend** (Django API) | http://localhost:8000    | `8000:8000`              |
| **Frontend** (app in browser) | http://localhost:3000 | `3000:80`                |

- **API base:** http://localhost:8000/api  
- **Admin:** http://localhost:8000/admin  
- **App (use this to take tests):** http://localhost:3000  

The frontend build uses `VITE_API_URL=http://localhost:8000/api` so the app talks to the backend on port 8000.

Create a superuser inside the backend container to use admin and login:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Flow

1. Log in (use Django superuser credentials).
2. Choose **Practice** or **Exam** mode.
3. Select a test (create tests and items in Django admin at `/admin/`).
4. Listen to audio, answer questions. In Practice you get instant feedback; in Exam you see the score report at the end.
5. Replay and focus-loss events are sent to the backend for anti-cheat.
