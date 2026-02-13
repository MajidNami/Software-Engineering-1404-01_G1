# Team13 - AI English Examination & Grading System
The **AI English Examination & Grading System** is a service in `team13` responsible for **delivering English exams and automatically evaluating student responses**. It administers **speaking and writing tests**, transcribes audio submissions, grades answers against standardized ETS scoring rubrics, and provides **detailed, multi-dimensional feedback**.
The system consists of **three main components**, all located in `team13`:
1. **Django API Server**
2. **Ollama LLM Service**
3. **Whisper ASR Service**
---
## 1. Django API Server
**Purpose:**
The **API server** is the core of the examination system. It manages the complete exam lifecycle — question delivery, response collection, and grading orchestration.
**Responsibilities:**
- Serve random writing and speaking questions to students.
- Track which questions each user has viewed.
- Accept text responses for writing exams.
- Accept audio files for speaking exams and transcribe them via Whisper.
- Build structured prompts and request grading from Ollama.
- Parse LLM responses and store detailed rubric-based scores.
- Generate comprehensive performance reports and analytics.

**Process example:**
1. Student requests a question via `GET /get_question/?type=writing`.
2. Server logs the view and returns question metadata.
3. Student submits answer via `POST /submit/`.
4. Server sends prompt to Ollama, receives structured JSON grade.
5. Server stores results in `WritingGradeResult` or `SpeakingGradeResult`.
6. Student receives immediate score and detailed feedback.

**Key point:**
The **Django server is the examination proctor** — it administers tests, collects responses, and coordinates AI grading.
---
## 2. Ollama LLM Service
**Purpose:**
The **Ollama service** is a dedicated container running `gemma3:4b`. It functions as the **expert examiner**, receiving grading prompts and returning **structured JSON evaluations** following official ETS rubric standards.

**Responsibilities:**
- Keep the LLM model loaded in memory for low-latency grading.
- Accept chat completion requests via HTTP API.
- Return scores (0-4), category scores, strengths, and improvement areas.

**Writing Rubric (0-4):**
- Task Achievement
- Coherence & Organization
- Vocabulary
- Grammar
- Mechanics

**Speaking Rubric (0-4):**
- Delivery
- Language Use
- Topic Development


**Key point:**
The **Ollama container is the examiner** — no business logic, just consistent, rubric-based grading.
---
## 3. Whisper ASR Service
**Purpose:**
The **Whisper service** is a dedicated container running OpenAI's Whisper `base` model. It serves as the **speaking test transcriber**, converting spoken responses into text for grading.

**Responsibilities:**
- Keep Whisper model loaded in memory for real-time transcription.
- Accept audio file uploads via HTTP API.
- Return transcribed text and detected language.

**Key point:**
The **Whisper container is the transcriptionist** — it converts speech to text so the examiner can grade it.
---
## Core Concept
The **AI English Examination & Grading System** exists to **deliver scalable, consistent, and immediate English proficiency assessment** for **speaking and writing** tests. By separating concerns into **specialized containers**, we achieve:
- **Modular architecture** — Each component does one thing well.
- **Consistent grading** — Standardized rubrics applied to every submission.
- **Immediate feedback** — Students receive scores and suggestions instantly.
- **Comprehensive analytics** — Track progress across all rubric categories.
---
## Summary of the Three Parts
- **Django API Server:** Serves questions, accepts submissions, orchestrates grading, stores results.
- **Ollama LLM Service:** Pure model container — receives prompts, returns structured grades.
- **Whisper ASR Service:** Pure model container — receives audio, returns transcription.
All three components in **`team13`** work together to deliver a **complete, automated English speaking and writing examination and grading system**.
