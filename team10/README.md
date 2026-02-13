# TOEFL Listening Practice - Full Stack Application

Complete TOEFL Listening practice application with Angular frontend and FastAPI backend.

## 📁 Project Structure

```
toefl-listening-project/
├── Backend/              # FastAPI backend
│   ├── app/             # Application code
│   ├── migrations/      # Database migrations
│   └── tests/           # Unit tests
├── Front/               # Angular frontend (add your code here)
├── static/              # Static files
├── templates/           # Email templates
├── .env.example         # Environment template
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
```

### 2. Backend Setup

```bash
cd Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd Front

# Add your Angular application here
# npm install
# ng serve
```

## 🛠️ Technology Stack

### Backend
- FastAPI 0.109.0
- Python 3.11+
- SQL Server 2019+
- PyODBC
- JWT Authentication

### Frontend
- Angular (your version)
- TypeScript
- RxJS

## 📖 Documentation

- Backend API will be available at: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## 🔧 Configuration

Edit `.env` file:
```env
DB_SERVER=localhost
DB_NAME=ToeflListeningDb
DB_USER=sa
DB_PASSWORD=YourPassword123
SECRET_KEY=your-secret-key
```

## 📝 Next Steps

1. Configure database connection
2. Add your Angular frontend to `Front/` directory
3. Add audio files to `static/ListeningItems/`
4. Run database migrations
5. Start both frontend and backend

## 📄 License

Private project for TOEFL Listening practice.
