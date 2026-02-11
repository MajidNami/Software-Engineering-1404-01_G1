# Team15 - TOEFL Reading Test & Practice API

Backend microservice for TOEFL Reading comprehension tests. Supports **Exam Mode** (timed, bulk submit, scored 0-30) and **Practice Mode** (per-question immediate feedback).

## Quick Start

### Local Development

```bash
source venv/bin/activate

# Run migrations
python manage.py makemigrations team15
python manage.py migrate --database=team15

# Load sample data (3 tests, 5 passages, 21 questions)
python manage.py load_mock_data

# Start server
python manage.py runserver
```

### Docker

```bash
# Create network (if not exists)
docker network create app404_net

# From team15/ directory
docker compose up --build
```

## Base URL

```
http://localhost:8000/team15/
```

---

## API Reference

### 1. List Tests

```
GET /team15/api/tests/
GET /team15/api/tests/?mode=exam
GET /team15/api/tests/?mode=practice
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "TOEFL Reading Practice Test 1",
    "mode": "practice",
    "time_limit": 0,
    "is_active": true,
    "passage_count": 2,
    "question_count": 7,
    "created_at": "2026-02-11T12:00:00Z"
  }
]
```

---

### 2. Test Detail

```
GET /team15/api/tests/{test_id}/
```

Returns the test with all passages and questions (choices included, correct answer excluded).

**Response:**
```json
{
  "id": 1,
  "title": "TOEFL Reading Practice Test 1",
  "mode": "practice",
  "time_limit": 0,
  "is_active": true,
  "passages": [
    {
      "id": 1,
      "title": "The History of Coffee",
      "content": "Coffee is one of the most...",
      "order": 1,
      "questions": [
        {
          "id": 1,
          "question_text": "According to the passage, who is credited with the discovery of coffee?",
          "question_type": "multiple_choice",
          "choices": ["A) A monastery abbot", "B) A goat herder named Kaldi", "C) Pope Clement VIII", "D) Yemeni traders"],
          "order": 1
        }
      ]
    }
  ],
  "created_at": "2026-02-11T12:00:00Z"
}
```

---

### 3. Start Attempt

```
POST /team15/api/attempts/start/
Content-Type: application/json
```

**Request:**
```json
{
  "test_id": 1,
  "user_id": "some-user-uuid"
}
```

**Response (201):**
```json
{
  "attempt_id": 1,
  "test_id": 1,
  "status": "in_progress",
  "started_at": "2026-02-11T12:00:00Z"
}
```

> If the user already has an in-progress attempt for this test, it returns the existing one instead of creating a new one.

---

### 4. Submit Answer (Practice Mode)

```
POST /team15/api/attempts/answer/
Content-Type: application/json
```

**Request:**
```json
{
  "attempt_id": 1,
  "question_id": 1,
  "selected_answer": "B) A goat herder named Kaldi"
}
```

**Response:**
```json
{
  "answer_id": 1,
  "is_correct": true,
  "correct_answer": "B) A goat herder named Kaldi",
  "selected_answer": "B) A goat herder named Kaldi"
}
```

> Returns immediate feedback. Can be called multiple times for the same question (updates the answer).

---

### 5. Bulk Submit (Exam Mode)

```
POST /team15/api/attempts/submit/
Content-Type: application/json
```

**Request:**
```json
{
  "attempt_id": 2,
  "answers": [
    {"question_id": 8, "selected_answer": "C) Cuneiform"},
    {"question_id": 9, "selected_answer": "B) Through simple pictures (pictographs)"},
    {"question_id": 10, "selected_answer": "C) Vowels"}
  ]
}
```

**Response:**
```json
{
  "attempt_id": 2,
  "score": 30,
  "accuracy": 100.0,
  "correct": 3,
  "total": 10,
  "status": "completed"
}
```

> Submits all answers at once, scores the attempt (0-30 scale), and marks it as completed. `total_time` is calculated automatically from `started_at`.

---

### 6. Finish Practice

```
POST /team15/api/attempts/finish/
Content-Type: application/json
```

**Request:**
```json
{
  "attempt_id": 1
}
```

**Response:**
```json
{
  "attempt_id": 1,
  "score": 15,
  "accuracy": 50.0,
  "correct": 1,
  "total": 2,
  "status": "completed"
}
```

> Call this after the user is done answering in practice mode. Scores and finalizes the attempt.

---

### 7. Attempt Result

```
GET /team15/api/attempts/{attempt_id}/result/
```

**Response:**
```json
{
  "id": 1,
  "test_title": "TOEFL Reading Practice Test 1",
  "test_mode": "practice",
  "status": "completed",
  "score": 15,
  "total_time": 120,
  "started_at": "2026-02-11T12:00:00Z",
  "finished_at": "2026-02-11T12:02:00Z",
  "accuracy": 50.0,
  "correct": 1,
  "total": 2,
  "answers": [
    {
      "id": 1,
      "question": {
        "id": 1,
        "question_text": "...",
        "question_type": "multiple_choice",
        "choices": ["A)", "B)", "C)", "D)"],
        "correct_answer": "B) A goat herder named Kaldi",
        "order": 1
      },
      "selected_answer": "B) A goat herder named Kaldi",
      "is_correct": true,
      "time_spent": null,
      "answered_at": "2026-02-11T12:01:00Z"
    }
  ]
}
```

---

### 8. User History

```
GET /team15/api/history/?user_id=some-user-uuid
```

**Response:**
```json
[
  {
    "id": 1,
    "test_title": "TOEFL Reading Practice Test 1",
    "test_mode": "practice",
    "status": "completed",
    "score": 15,
    "total_time": 120,
    "started_at": "2026-02-11T12:00:00Z",
    "finished_at": "2026-02-11T12:02:00Z"
  }
]
```

---

### 9. User Dashboard

```
GET /team15/api/dashboard/?user_id=some-user-uuid
```

**Response:**
```json
{
  "user_id": "some-user-uuid",
  "total_attempts": 5,
  "completed_attempts": 3,
  "in_progress_attempts": 2,
  "average_score": 22.3
}
```

---

## Typical Frontend Flows

### Practice Mode
1. `GET /api/tests/?mode=practice` — show test list
2. User picks a test → `GET /api/tests/{id}/` — get passages & questions
3. `POST /api/attempts/start/` — start attempt
4. For each question → `POST /api/attempts/answer/` — get immediate feedback
5. When done → `POST /api/attempts/finish/` — get final score
6. `GET /api/attempts/{id}/result/` — show detailed results

### Exam Mode
1. `GET /api/tests/?mode=exam` — show test list
2. User picks a test → `GET /api/tests/{id}/` — get passages & questions + `time_limit`
3. `POST /api/attempts/start/` — start attempt, begin countdown timer
4. User answers all questions locally
5. `POST /api/attempts/submit/` — bulk submit all answers at once
6. `GET /api/attempts/{id}/result/` — show detailed results

## Scoring

Score is scaled to **0-30** (TOEFL Reading scale):
- `score = round((correct / total) * 30)`
- `accuracy = (correct / total) * 100`

## Error Responses

All errors follow this format:
```json
{"detail": "Error message here"}
```

| Status | Meaning                               |
|--------|---------------------------------------|
| 400    | Bad request / missing required fields |
| 404    | Test, attempt, or question not found  |

## Mock Data

3 tests are pre-loaded:

| ID|  Title                          | Mode     | Time Limit | Passages | Questions |
|---|---------------------------------|----------|------------|----------|-----------|
| 1 | TOEFL Reading Practice Test 1   | practice | none       | 2        | 7         |
| 2 | TOEFL Reading Exam Simulation 1 | exam     | 36 min     | 2        | 10        |
| 3 | TOEFL Reading Practice Test 2   | practice | none       | 1        | 4         |

Reload mock data: `python manage.py load_mock_data --clear`
