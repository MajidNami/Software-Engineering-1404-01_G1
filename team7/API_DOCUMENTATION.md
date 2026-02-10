# Team7 TOEFL AI Evaluation Platform - API Documentation

## Overview
This document provides complete API specifications for frontend integration with the Team7 TOEFL AI Evaluation microservice.

**Base URL**: `http://localhost:8000/team7/`  
**API Version**: v1  
**Authentication**: Bearer Token (JWT) via `Authorization` header  
**Content-Type**: `application/json` (except file uploads use `multipart/form-data`)

---

## Table of Contents
1. [Authentication](#authentication)
2. [Writing Evaluation API](#writing-evaluation-api)
3. [Speaking Evaluation API](#speaking-evaluation-api)
4. [History API](#history-api)
5. [Analytics API](#analytics-api)
6. [Admin Health API](#admin-health-api)
7. [Error Codes](#error-codes)
8. [Models & Data Structures](#models--data-structures)

---

## Authentication

All API endpoints (except HTML views) require authentication via Bearer token.

### Headers
```http
Authorization: Bearer <your-jwt-token>
```

### Example
```javascript
fetch('http://localhost:8000/team7/api/v1/evaluate/writing/', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

---

## Writing Evaluation API

### Submit Writing Task

**Endpoint**: `POST /api/v1/evaluate/writing/`  
**Description**: Submit student essay for AI evaluation  
**Use Case**: UC-01, FR-WR

#### Request

```javascript
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "question_id": "650e8400-e29b-41d4-a716-446655440001",
    "text": "Technology has revolutionized modern education..."
}
```

**Fields**:
- `user_id` (string, required): UUID of the student
- `question_id` (string, required): UUID of the question being answered
- `text` (string, required): Essay text (50-1000 words)

#### Response (200 OK)

```javascript
{
    "status": "success",
    "evaluation_id": "750e8400-e29b-41d4-a716-446655440002",
    "overall_score": 4.5,
    "feedback": "Your essay demonstrates strong organization and clear arguments. Consider expanding your examples with more specific details to strengthen your topic development.",
    "criteria": [
        {
            "name": "Grammar",
            "score": 4.5,
            "comment": "Excellent grammar with only minor errors"
        },
        {
            "name": "Vocabulary",
            "score": 4.0,
            "comment": "Good vocabulary range, appropriate for academic writing"
        },
        {
            "name": "Organization",
            "score": 5.0,
            "comment": "Clear structure with well-developed paragraphs"
        },
        {
            "name": "Topic Development",
            "score": 4.5,
            "comment": "Strong main ideas with relevant supporting examples"
        }
    ],
    "created_at": "2024-02-09T10:30:00Z"
}
```

#### Error Responses

**400 - Invalid Input**
```javascript
{
    "error": "INVALID_INPUT: Text is too short (minimum 50 words).",
    "code": "INVALID_INPUT"
}
```

**404 - Question Not Found**
```javascript
{
    "error": "QUESTION_NOT_FOUND",
    "message": "Invalid question ID"
}
```

**503 - Service Unavailable**
```javascript
{
    "error": "SERVICE_UNAVAILABLE",
    "message": "AI service temporarily unavailable. Try again later."
}
```

---

## Speaking Evaluation API

### Submit Speaking Task

**Endpoint**: `POST /api/v1/evaluate/speaking/`  
**Description**: Submit audio recording for AI evaluation  
**Use Case**: UC-02, FR-SP  
**Content-Type**: `multipart/form-data`

#### Request

**Form Fields**:
- `user_id` (string, required): UUID of the student
- `question_id` (string, required): UUID of the question
- `audio_file` (file, required): Audio file (.wav, .mp3, .flac, max 10MB)

#### cURL Example
```bash
curl -X POST http://localhost:8000/team7/api/v1/evaluate/speaking/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "user_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "question_id=650e8400-e29b-41d4-a716-446655440001" \
  -F "audio_file=@recording.wav"
```

#### JavaScript Example
```javascript
const formData = new FormData();
formData.append('user_id', userId);
formData.append('question_id', questionId);
formData.append('audio_file', audioBlob, 'recording.wav');

fetch('http://localhost:8000/team7/api/v1/evaluate/speaking/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    },
    body: formData
});
```

#### Response (200 OK)

```javascript
{
    "status": "success",
    "evaluation_id": "850e8400-e29b-41d4-a716-446655440003",
    "overall_score": 3.5,
    "feedback": "Your response demonstrates good language control with clear pronunciation. Try to speak more naturally and expand on your ideas with additional examples.",
    "transcript": "In my opinion, technology has greatly improved education by providing access to online resources and interactive learning tools. For example, students can now watch educational videos and participate in virtual classrooms...",
    "criteria": [
        {
            "name": "Delivery",
            "score": 3.5,
            "comment": "Clear pronunciation with good pace, minor hesitations"
        },
        {
            "name": "Language Use",
            "score": 3.5,
            "comment": "Appropriate vocabulary with mostly correct grammar"
        },
        {
            "name": "Topic Development",
            "score": 3.0,
            "comment": "Good main idea but could expand with more details"
        }
    ],
    "created_at": "2024-02-09T10:35:00Z"
}
```

#### Error Responses

**400 - Invalid File**
```javascript
{
    "error": "INVALID_INPUT: File format '.txt' not supported. Use .wav, .mp3, .flac.",
    "code": "INVALID_INPUT"
}
```

**400 - No Speech Detected**
```javascript
{
    "error": "NO_SPEECH_DETECTED",
    "message": "No speech detected in the audio file. Please ensure your microphone is working."
}
```

**400 - File Too Large**
```javascript
{
    "error": "INVALID_INPUT: File size (12.5MB) exceeds limit of 10MB.",
    "code": "INVALID_INPUT"
}
```

---

## History API

### Get Evaluation History

**Endpoint**: `GET /api/v1/history/` or `GET /api/v1/history/<user_id>/`  
**Description**: Retrieve past evaluations for a student  
**Use Case**: UC-03

#### Query Parameters
- `limit` (integer, optional): Max records to return (default: 50)

#### Request Example
```javascript
GET /api/v1/history/?limit=20
```

#### Response (200 OK)

```javascript
{
    "status": "success",
    "total_attempts": 15,
    "attempts": [
        {
            "evaluation_id": "950e8400-e29b-41d4-a716-446655440004",
            "task_type": "writing",
            "question_id": "650e8400-e29b-41d4-a716-446655440001",
            "overall_score": 4.5,
            "created_at": "2024-02-09T10:30:00Z",
            "criteria": [
                {"name": "Grammar", "score": 4.5},
                {"name": "Vocabulary", "score": 4.0},
                {"name": "Organization", "score": 5.0},
                {"name": "Topic Development", "score": 4.5}
            ]
        },
        {
            "evaluation_id": "a50e8400-e29b-41d4-a716-446655440005",
            "task_type": "speaking",
            "question_id": "750e8400-e29b-41d4-a716-446655440002",
            "overall_score": 3.5,
            "created_at": "2024-02-08T14:20:00Z",
            "criteria": [
                {"name": "Delivery", "score": 3.5},
                {"name": "Language Use", "score": 3.5},
                {"name": "Topic Development", "score": 3.0}
            ]
        }
    ]
}
```

#### Response (200 OK - No Data)

```javascript
{
    "status": "no_data",
    "message": "No attempts yet. Start a practice test!",
    "attempts": []
}
```

---

## Analytics API

### Get Analytics with Trends

**Endpoint**: `GET /api/v1/analytics/` or `GET /api/v1/analytics/<user_id>/`  
**Description**: Retrieve evaluation history with statistical analysis and trends  
**Use Case**: UC-03, FR-MON-02

#### Query Parameters
- `limit` (integer, optional): Max records to analyze (default: 50)

#### Request Example
```javascript
GET /api/v1/analytics/?limit=30
```

#### Response (200 OK)

```javascript
{
    "status": "success",
    "total_attempts": 15,
    "attempts": [
        // Same structure as History API
    ],
    "analytics": {
        "overall": {
            "statistics": {
                "mean": 4.1,
                "min": 3.0,
                "max": 5.0,
                "median": 4.0,
                "count": 15
            },
            "improvement": {
                "improvement": 15.5,
                "trend": "improving"
            },
            "moving_average": [null, null, 3.8, 4.0, 4.2, 4.1, ...]
        },
        "writing": {
            "statistics": {
                "mean": 4.3,
                "min": 3.5,
                "max": 5.0,
                "median": 4.5,
                "count": 8
            },
            "improvement": {
                "improvement": 20.0,
                "trend": "improving"
            }
        },
        "speaking": {
            "statistics": {
                "mean": 3.5,
                "min": 3.0,
                "max": 4.0,
                "median": 3.5,
                "count": 7
            },
            "improvement": {
                "improvement": 10.0,
                "trend": "improving"
            }
        }
    }
}
```

#### Analytics Fields Explained

**statistics**:
- `mean`: Average score across all attempts
- `min`: Lowest score
- `max`: Highest score
- `median`: Middle value when sorted
- `count`: Total number of evaluations

**improvement**:
- `improvement`: Percentage change from first to last score
- `trend`: One of: `"improving"` (>5%), `"stable"` (±5%), `"declining"` (<-5%), `"insufficient_data"` (<2 scores)

**moving_average**:
- 3-point moving average for trend smoothing
- First 2 values are `null` (insufficient data)
- Use for chart visualization

---

## Admin Health API

### Get System Health

**Endpoint**: `GET /api/v1/admin/health/`  
**Description**: Comprehensive system health monitoring for admins  
**Use Case**: UC-04, FR-MON, NFR-AVAIL-01  
**Authentication**: Admin role required

#### Response (200 OK - Healthy)

```javascript
{
    "service": "team7",
    "timestamp": "2024-02-09T15:30:00Z",
    "status": "healthy",
    "checks": {
        "database": {
            "status": "healthy",
            "message": "Database connection successful"
        },
        "llm_service": {
            "status": "healthy",
            "message": "LLM API accessible",
            "models_available": 5
        },
        "api_performance": {
            "status": "healthy",
            "total_requests_24h": 1250,
            "error_requests_24h": 45,
            "error_rate": 3.6,
            "avg_latency_ms": 1850.5,
            "slowest_endpoints": [
                {
                    "endpoint": "/api/v1/evaluate/speaking/",
                    "avg_latency": 4200.0,
                    "count": 85
                },
                {
                    "endpoint": "/api/v1/evaluate/writing/",
                    "avg_latency": 2100.0,
                    "count": 120
                }
            ]
        },
        "database_stats": {
            "status": "info",
            "total_evaluations": 3450,
            "total_questions": 25,
            "evaluations_today": 42
        }
    }
}
```

#### Response (200 OK - Degraded)

```javascript
{
    "service": "team7",
    "timestamp": "2024-02-09T15:30:00Z",
    "status": "degraded",
    "checks": {
        "database": {
            "status": "healthy",
            "message": "Database connection successful"
        },
        "llm_service": {
            "status": "unhealthy",
            "message": "LLM service error: Connection timeout"
        },
        "api_performance": {
            "status": "degraded",
            "total_requests_24h": 1250,
            "error_requests_24h": 150,
            "error_rate": 12.0,
            "avg_latency_ms": 6500.0
        }
    }
}
```

#### Response (503 - Unhealthy)

```javascript
{
    "service": "team7",
    "timestamp": "2024-02-09T15:30:00Z",
    "status": "unhealthy",
    "checks": {
        "database": {
            "status": "unhealthy",
            "message": "Database error: Connection refused"
        },
        "api_performance": {
            "status": "degraded",
            "error_rate": 45.0
        }
    }
}
```

#### Status Codes
- **200**: System is `healthy` or `degraded` (still operational)
- **503**: System is `unhealthy` (critical failure)

---

## Error Codes

### Standard Error Response Format
```javascript
{
    "error": "ERROR_CODE",
    "message": "Human-readable error description"
}
```

### Error Code Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Missing required fields, invalid format, or out of bounds |
| `QUESTION_NOT_FOUND` | 404 | Question ID does not exist |
| `NO_SPEECH_DETECTED` | 400 | Audio file contains no detectable speech |
| `SERVICE_UNAVAILABLE` | 503 | External AI service (LLM/ASR) is down |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `UNAUTHENTICATED` | 401 | Missing or invalid authentication token |
| `PERMISSION_DENIED` | 403 | Valid token but insufficient permissions |

---

## Models & Data Structures

### Evaluation Object
```typescript
interface Evaluation {
    evaluation_id: string;          // UUID
    task_type: "writing" | "speaking";
    question_id: string;            // UUID
    overall_score: number;          // 0.0 - 5.0 (writing) or 0.0 - 4.0 (speaking)
    created_at: string;             // ISO 8601 timestamp
    criteria: CriterionScore[];
}
```

### Criterion Score
```typescript
interface CriterionScore {
    name: string;                   // e.g., "Grammar", "Delivery"
    score: number;                  // 0.0 - 5.0 or 0.0 - 4.0
    comment?: string;               // Optional feedback
}
```

### Analytics Object
```typescript
interface Analytics {
    overall: TaskAnalytics;
    writing: TaskAnalytics | null;
    speaking: TaskAnalytics | null;
}

interface TaskAnalytics {
    statistics: {
        mean: number;
        min: number;
        max: number;
        median: number;
        count: number;
    };
    improvement: {
        improvement: number;        // Percentage (-100 to +∞)
        trend: "improving" | "declining" | "stable" | "insufficient_data";
    };
    moving_average?: (number | null)[];
}
```

---

## Performance Expectations

### Response Times (SRS NFR)
- **Writing Evaluation**: < 15 seconds (95th percentile)
- **Speaking Evaluation**: < 25 seconds (95th percentile)
- **History/Analytics**: < 2 seconds
- **Health Check**: < 1 second

### Rate Limits
- Not currently enforced
- Recommended: 100 requests per user per hour

### File Size Limits
- **Audio Files**: 10MB maximum
- **Text Submissions**: 1000 words maximum

---

## Frontend Implementation Examples

### React Example - Writing Submission

```javascript
const submitWriting = async (userId, questionId, text) => {
    try {
        const response = await fetch('http://localhost:8000/team7/api/v1/evaluate/writing/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                question_id: questionId,
                text: text
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Submission failed');
        }

        return data;
    } catch (error) {
        console.error('Writing submission error:', error);
        throw error;
    }
};
```

### React Example - Audio Recording & Speaking Submission

```javascript
const recordAndSubmit = async (userId, questionId) => {
    // Start recording
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const chunks = [];

    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        
        // Submit to API
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('question_id', questionId);
        formData.append('audio_file', audioBlob, 'recording.wav');

        const response = await fetch('http://localhost:8000/team7/api/v1/evaluate/speaking/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: formData
        });

        return response.json();
    };

    mediaRecorder.start();
    
    // Stop after 60 seconds or manually
    setTimeout(() => mediaRecorder.stop(), 60000);
};
```

### Chart.js Example - Analytics Visualization

```javascript
const renderAnalyticsChart = (analyticsData) => {
    const ctx = document.getElementById('progressChart').getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: analyticsData.attempts.map(a => 
                new Date(a.created_at).toLocaleDateString()
            ),
            datasets: [
                {
                    label: 'Overall Score',
                    data: analyticsData.attempts.map(a => a.overall_score),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                },
                {
                    label: 'Moving Average',
                    data: analyticsData.analytics.overall.moving_average,
                    borderColor: 'rgb(255, 99, 132)',
                    borderDash: [5, 5],
                    tension: 0.1
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5
                }
            }
        }
    });
};
```

---

## Changelog

### v1.0.0 (2024-02-09)
- Initial API release
- Writing evaluation endpoint
- Speaking evaluation endpoint
- History and analytics endpoints
- Admin health monitoring

---

## Support

For API issues or questions, contact:
- **Developer**: Mahan Zavari (Backend & AI)
- **Team**: Team 7
- **Documentation**: This file

**Note**: This API follows REST principles and returns standard HTTP status codes. Always check the status code before processing the response body.
