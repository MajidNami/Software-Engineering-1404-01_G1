# Project Instructions for Codex (Team12)

## Scope
- Only edit files under: team12/
- Do not modify other teams or core unless explicitly asked.

## Goal
Implement Team12 Listening microservice (Exam + Practice) in Django.

## Key routes
All Team12 routes live under /team12/...

## Dev workflow
- Run: python manage.py check
- Run: python manage.py test team12

## Requirements summary
- Practice: allow replay; show correct answer + explanation.
- Exam: forbid pause/seek/replay; track focus-lost; mark session suspicious after repeated focus loss.
- Persist: sessions, answers with timestamps/time_spent, event logs.
- Provide minimal admin CRUD for listening tests + questions.
