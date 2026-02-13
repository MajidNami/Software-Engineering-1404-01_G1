# Team 7 - TOEFL AI Evaluation Microservice

## Overview
This microservice provides automated evaluation for TOEFL Writing and Speaking tasks using Large Language Models (LLM) and Automatic Speech Recognition (ASR).

## Architecture
- **Tech Stack**: Django 4.2+, PostgreSQL/SQLite, OpenAI API (GPT + Whisper)
- **Pattern**: 3-Layer Architecture (Controller → Service → Repository)
- **Deployment**: Docker + Nginx Gateway

## Backend Setup 

### 1. Database Schema
All models have been created and migrated:

- **Question**: Stores TOEFL practice questions
  - Fields: `question_id` (UUID), `prompt_text`, `task_type` (writing/speaking), `mode` (independent/integrated), `difficulty` (1-5)
  
- **Evaluation**: Stores student submissions and AI results
  - Fields: `evaluation_id` (UUID), `user_id`, `question_id` (FK), `submitted_text`, `audio_path`, `overall_score`, `ai_feedback`, `transcript_text`, `rubric_version_id`, `created_at`
  - Indexed on: `user_id` + `created_at` for fast history queries
  
- **DetailedScore**: Stores criterion-level scores
  - Fields: `score_id` (UUID), `evaluation_id` (FK), `criterion` (e.g., 'Grammar'), `score_value` (0.0-5.0), `comment`

### 2. Sample Data
The database has been seeded with **11 TOEFL questions**:
- 5 Writing tasks (3 independent, 2 integrated)
- 6 Speaking tasks (4 independent, 2 integrated)
- Difficulty range: 1-5

**Run migrations and seed data:**
```bash
python manage.py migrate team7 --database=team7
python manage.py seed_questions
```

**Verify setup:**
```bash
python team7/test_db.py
```

### 3. Service Layer

#### WritingEvaluator (`services.py`)
- Validates word count (50-1000 words per SRS FR-WR-01)
- Constructs prompts with ETS TOEFL iBT rubric
- Sends to LLM for analysis
- Parses JSON response with scores and feedback
- **Performance Target**: < 15 seconds response time

#### SpeakingEvaluator (`services.py`)
- Validates audio format (.wav, .mp3, .flac) and size (max 10MB)
- Transcribes audio using OpenAI Whisper ASR
- Checks for speech detection (prevents wasted LLM calls on silence)
- Analyzes transcript for Delivery, Language Use, Topic Development
- **Performance Target**: < 25 seconds response time

#### EvaluationService (`services.py`)
- Orchestrates Writing and Speaking evaluators
- Handles database persistence
- Implements analytics for progress tracking

### 4. API Endpoints

All endpoints follow RESTful conventions and require authentication:

| Endpoint | Method | Purpose | SRS Ref |
|----------|--------|---------|---------|
| `/team7/api/v1/evaluate/writing/` | POST | Submit essay for evaluation | UC-01, FR-WR |
| `/team7/api/v1/evaluate/speaking/` | POST | Submit audio for evaluation | UC-02, FR-SP |
| `/team7/api/v1/history/` | GET | Get user's evaluation history | UC-03, FR-MON |
| `/team7/ping/` | GET | Health check | FR-API-01 |

**Example Writing Request:**
```json
POST /team7/api/v1/evaluate/writing/
{
  "user_id": "uuid-here",
  "question_id": "uuid-here",
  "text": "Your essay content..."
}
```

**Example Response:**
```json
{
  "evaluation_id": "uuid",
  "overall_score": 4.2,
  "feedback": "Your essay demonstrates...",
  "criteria": [
    {"name": "Grammar", "score": 4.0, "comment": "..."},
    {"name": "Vocabulary", "score": 4.5, "comment": "..."}
  ]
}
```

### 5. Admin Panel
Django admin configured for monitoring:
- Question management (create/edit TOEFL questions)
- Evaluation monitoring (view submitted evaluations, read-only)
- DetailedScore inline display

Access at: `http://localhost:8000/admin/`

## Docker Configuration 

### Dockerfile
Located at `team7/Dockerfile` (for reference only; main deployment uses root Dockerfile)
- Base: `python:3.12-slim`
- Installs: MySQL client, OpenAI SDK, Django dependencies
- Auto-migration on container start

### docker-compose.yml
Simplified per deployment guidelines:
- **Gateway service**: Nginx proxy on `${TEAM_PORT}`
- Routes all requests to core Django (`http://core:8000`)
- Preserves authentication cookies
- Network: `app404_net` (external)

**Run team7 service:**
```bash
# From project root
./linux_scripts/up-team.sh 7
```

### gateway.conf
Nginx configuration with:
- Cookie forwarding for authentication (FR-SEC)
- Extended read timeout (60s) for AI processing
- Proper headers for proxying

## Environment Configuration 

### Required Environment Variables
Add to `.env` at project root:

```bash
# Team 7 Database (local SQLite for dev)
TEAM7_DATABASE_URL=sqlite:///team7/team7.sqlite3

# AI Services (REQUIRED for functionality)
AI_GENERATOR_API_KEY=your-openai-api-key-here
```

**Get OpenAI API Key**: https://platform.openai.com/api-keys

### Production Database
For cloud MySQL deployment, update:
```bash
TEAM7_DATABASE_URL=mysql://team7_user:team7_pass@HOST:PORT/DBNAME
```

## Testing

### Unit Tests
Located at `team7/tests.py`:
```bash
python manage.py test team7
```

### API Tests
- `team7/test_api.py`: Writing evaluation tests
- `team7/test_speaking_api.py`: Speaking evaluation tests

### Database Verification
```bash
python team7/test_db.py
```

## Compliance with Documentation

### SRS Requirements (srs.txt)
-  FR-WR-01: Word count validation (50-1000)
-  FR-WR-05: Actionable feedback generation
-  FR-SP-01: Audio format and size validation
-  FR-API-01: Health check endpoint
-  FR-API-02: Unified evaluation endpoint with mode parameter
-  FR-SEC-01: SQL injection and XSS protection (Django ORM + validation)
-  NFR-REL-01: Database indexes for performance

### Architecture (arch.txt)
-  3-Layer Architecture implemented
-  Controller Layer: `views.py` (EvaluationController, AuthController)
-  Service Layer: `services.py` (WritingEvaluator, SpeakingEvaluator, EvaluationService)
-  Repository Layer: Django ORM with `models.py`

### Diagrams (diagrams.txt)
-  ER Diagram: All tables created (users handled by core, questions, evaluations, detailed_scores)
-  Class Diagram: Service classes implemented
-  Sequence Diagrams: API flows implemented in views

### Deployment (deployment.txt)
-  Docker configuration per Section 5-6
-  Database routing configured (Section 7)
-  Gateway Nginx setup (Section 6)
-  Team-specific database URL support

### Tasks (tasks.txt)
#### Mahan Zavari (Backend & AI) - Sprint 1-2
-  Task 1: Database Schema Implementation
-  Task 2: Writing Evaluation Service Logic
-  Task 3: Writing API Endpoints
-  Task 8: ASR Service Integration
-  Task 9: Speaking Evaluation Logic
-  Task 10: Speaking API Endpoint

#### Infrastructure
-  Docker and docker-compose setup
-  Database migrations
-  Sample data seeding
-  Environment configuration

## Next Steps (Frontend Integration - Sprint 3)

1. **Writing Interface** (Amin Rezaeeyan)
   - HTML form for essay submission
   - AJAX call to `/team7/api/v1/evaluate/writing/`
   - Display results with score breakdown

2. **Speaking Interface** (Amin Rezaeeyan)
   - Audio recorder component (MediaRecorder API)
   - Upload to `/team7/api/v1/evaluate/speaking/`
   - Display transcript + scores

3. **Dashboard** (Amin + Mohammad)
   - Fetch history from `/team7/api/v1/history/`
   - Chart.js visualization
   - Trend analysis display

4. **Testing** (Mohammad Yarahmadi)
   - Integration tests
   - Load testing
   - Performance optimization

## Troubleshooting

### Database Issues
```bash
# Reset database
rm team7/team7.sqlite3
python manage.py migrate team7 --database=team7
python manage.py seed_questions
```

### Docker Issues
```bash
# Rebuild containers
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### API Key Issues
Ensure `AI_GENERATOR_API_KEY` is set in `.env`. The service uses a fallback placeholder but requires a real key for functionality.

## Repository Structure
```
team7/
├── admin.py              # Django admin configuration
├── apps.py               # App configuration
├── models.py             # Database models (Question, Evaluation, DetailedScore)
├── services.py           # Business logic (WritingEvaluator, SpeakingEvaluator)
├── views.py              # API controllers
├── urls.py               # URL routing
├── tests.py              # Unit tests
├── test_db.py            # Database verification script
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Service orchestration
├── gateway.conf          # Nginx configuration
├── requirements.txt      # Python dependencies
├── management/           # Management commands
│   └── commands/
│       └── seed_questions.py
├── migrations/           # Database migrations
├── static/               # CSS/JS assets
└── templates/            # HTML templates
```

## Contact
- **Backend Lead**: Mahan Zavari
- **Frontend Lead**: Amin Rezaeeyan
- **QA Lead**: Mohammad Yarahmadi

---

**Status**:  Backend Complete |  Frontend In Progress
