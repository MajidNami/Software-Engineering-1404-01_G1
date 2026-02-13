# TOEFL Listening Practice - Full Stack Application

Complete TOEFL Listening practice application with Angular frontend and FastAPI backend.

## 📁 Project Structure

```
toefl-listening-project/
├── Backend/                        # FastAPI backend
│   ├── app/                       # Application code
│   │   ├── api/                   # API endpoints
│   │   ├── core/                  # Core configurations
│   │   ├── db/                    # Database connection
│   │   ├── models/                # Data models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/              # Business logic
│   │   └── main.py                # Application entry
│   ├── migrations/                # Database migrations
│   ├── tests/                     # Unit tests
│   ├── Dockerfile                 # Backend container
│   └── requirements.txt           # Python dependencies
├── Front/                         # Angular frontend (add your code)
├── static/                        # Static files (audio)
│   └── ListeningItems/            # Audio files here
├── templates/                     # Email templates
├── docker-compose.yml             # Service orchestration
├── gateway.conf                   # Nginx configuration
├── .env.example                   # Environment template
├── Creating-DataBase-Tables.sql   # Database schema
├── Inserting-Data.sql             # Sample data
└── README.md                      # This file
```

## 🚀 Quick Start with Docker

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your database password

# 2. Add your Angular app to Front/ directory

# 3. Add audio files to static/ListeningItems/

# 4. Start all services
docker-compose up -d

# 5. Run database migrations
docker-compose exec backend python migrations/run_migration.py

# 6. Access your app
# Frontend: http://localhost
# Backend API: http://localhost/api
# API Docs: http://localhost:8000/api/docs
```

## 📡 API Endpoints

- `POST /api/users/register` - Register
- `POST /api/users/login` - Login
- `GET /api/exercises/listening` - Get exercises
- `POST /api/exercises/listening/submit` - Submit answers
- Full API docs at: http://localhost:8000/api/docs

## 🛠️ Local Development

### Backend
```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd Front
npm install
ng serve
```

## 📝 Configuration

Edit `.env`:
```env
DB_PASSWORD=YourStrongPassword123!
SECRET_KEY=your-secret-key-min-32-chars
```

## 🎯 Next Steps

1. Add your Angular app to `Front/`
2. Add audio files to `static/ListeningItems/`
3. Run `docker-compose up -d`
4. Visit http://localhost

See full documentation in this README for details!
