# Team 11 - TOEFL Listening & Writing Assessment

AI-powered English exam microservice with dynamic question system and TOEFL iBT-standard assessment.

[View Figma Design](https://www.figma.com/design/3uaZuwIjT0OU8v7w2cy7Df/SE1_T11?node-id=0-1&m=dev&t=wTZc2qAKki3quDGV-1)

## Features

**AI Assessment** (Deepseek + Whisper)
- Writing: Grammar, Vocabulary, Coherence, Task Response (TOEFL iBT rubric)
- Speaking: Delivery, Fluency, Vocabulary, Grammar, Topic Development (TOEFL iBT rubric)
- Audio transcription with Whisper API
- Personalized feedback with improvement suggestions
- Cost: ~$0.10/month for 300 submissions

**Dynamic Question System**
- Category-based question organization (Academic, Personal, Opinion, etc.)
- Random question selection per exam
- Difficulty levels: beginner, intermediate, advanced
- 10 sample TOEFL-style questions included

**Database Models**
- `QuestionCategory` & `Question`: Dynamic question management
- `Submission`: Base model with status tracking
- `WritingSubmission` & `ListeningSubmission`: Exam details with question linking
- `AssessmentResult`: Detailed TOEFL-standard scores and feedback

## Quick Start

**Local Development:**
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate --database=team11
python manage.py runserver
```
Access: http://localhost:8000/team11/

**Docker:**
```powershell
docker-compose up --build
docker-compose exec core python manage.py migrate
```

## AI Integration

**API Configuration:**
- Provider: GapGPT (`https://api.gapgpt.app/v1`)
- Models: `deepseek-chat` (text), `gapgpt/whisper-1` (audio)
- Key: Configured in `services/ai_service.py`

**Service Layer:**
```python
from team11.services import assess_writing, assess_speaking

# Writing: Returns scores + feedback
result = assess_writing(topic, text_body, word_count)

# Speaking: Transcription + analysis
result = assess_speaking(topic, audio_file_path, duration_seconds)
```

**Test AI:**
```powershell
python team11/test_ai_service.py
```

## TOEFL iBT Assessment Criteria

**Writing** (0-100 scale, normalized from 5-point rubric):
| Score | Grammar & Syntax | Vocabulary | Coherence | Task Response |
|-------|------------------|------------|-----------|---------------|
| 90-100 | Minimal errors, clear | Precise, varied | Well-organized | Fully developed |
| 70-89 | Minor errors | Adequate variety | Generally clear | Somewhat developed |
| 50-69 | Frequent errors | Limited range | Basic organization | Limited development |
| 30-49 | Severe errors | Repetitive | Disorganized | Poorly developed |
| 0-29 | Unintelligible | Severely limited | Incoherent | Minimal response |

**Speaking** (0-100 scale, normalized from 4-point rubric):
| Score | Delivery | Fluency | Vocabulary | Grammar | Development |
|-------|----------|---------|------------|---------|-------------|
| 85-100 | Clear speech | Minor hesitation | Effective | Good control | Fully developed |
| 60-84 | Generally clear | Some hesitation | Adequate | Noticeable errors | Somewhat developed |
| 35-59 | Unclear | Frequent pauses | Limited | Frequent errors | Limited development |
| 0-34 | Hard to understand | Fragmented | Severely limited | Severe errors | Minimal content |

## Project Structure

```
team11/
├── services/
│   ├── ai_service.py       # AI assessment functions
│   └── prompts.py          # TOEFL iBT prompts
├── models.py               # Database schema
├── views.py                # API endpoints (dynamic questions)
├── admin.py                # Admin interface for questions
├── migrations/             # Database migrations
├── templates/team11/       # Frontend templates
└── test_ai_service.py      # AI testing
```

## Testing

1. **Register**: http://localhost:8000/ → ثبت نام
2. **Writing Exam**: Select category → Random question appears → Submit essay (150+ words)
3. **Speaking Exam**: Select category → Random question appears → Record audio (30-60s)
4. **Dashboard**: View all submissions and detailed TOEFL-standard scores
5. **Admin**: http://localhost:8000/admin/ → Manage questions and categories

## API Endpoints

- `POST /team11/api/submit-writing/` - Submit writing with question_id
- `POST /team11/api/submit-listening/` - Submit speaking with question_id
- `GET /team11/dashboard/` - Submission history
- `GET /team11/submission/<uuid>/` - Detailed results

## Architecture

- **Microservice Pattern**: Independent database (`team11.sqlite3`)
- **Authentication**: Shared JWT cookies via core app
- **AI Service**: Isolated in `services/` layer
- **Database Router**: Custom routing for team databases
- **Error Handling**: Failed assessments logged with status='failed'

---
**Team 11** - Software Engineering 1404-01 | Amirkabir University of Technology
