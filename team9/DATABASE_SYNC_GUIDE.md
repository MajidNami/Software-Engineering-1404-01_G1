# Database Synchronization Guide for Team9 Vocabulary App

**Author:** Senior Django Architect  
**Date:** 2026-02-05  
**Language:** English (Project Standard)

---

## Table of Contents

1. [Overview](#overview)
2. [Problem Description](#problem-description)
3. [Solution Architecture](#solution-architecture)
4. [Quick Start](#quick-start)
5. [Manual Step-by-Step Guide](#manual-step-by-step-guide)
6. [Conflict Resolution](#conflict-resolution)
7. [Troubleshooting](#troubleshooting)
8. [Files Created](#files-created)

---

## Overview

This guide provides a comprehensive solution for synchronizing the Django database for the Team9 Vocabulary App, ensuring all models have corresponding tables and the database is populated with realistic test data.

### Key Features

- ✅ **Dynamic Model Discovery**: Automatically detects all models using `apps.get_models()`
- ✅ **Automated Superuser Creation**: Creates admin user for Django admin panel
- ✅ **Realistic Test Data**: Populates database with lessons, words, and progress tracking
- ✅ **Conflict Resolution**: Handles migration conflicts and provides clean slate option
- ✅ **Cross-Platform**: Scripts provided for both Windows and Linux/Mac

---

## Problem Description

### Common Issues

1. **OperationalError**: Database tables missing for models
2. **Migration Conflicts**: Local migrations differ from teammate's code
3. **Empty Database**: No test data for frontend development
4. **Manual Setup Pain**: Tedious process to create superuser and seed data

### Root Causes

- Models created but migrations not generated/applied
- Team members working on different branches with conflicting migrations
- Database file not synchronized across environments
- Missing initial data setup

---

## Solution Architecture

### Components Created

1. **`setup_and_seed.py`** - Main Python script
   - Discovers all models dynamically
   - Verifies table existence
   - Runs migrations
   - Creates superuser
   - Seeds realistic test data

2. **`reset_database.bat`** - Windows reset script
   - Backs up existing database
   - Cleans old migrations
   - Creates fresh migrations
   - Runs setup and seed

3. **`reset_database.sh`** - Linux/Mac reset script
   - Same functionality as .bat for Unix systems

---

## Quick Start

### Option 1: Fresh Setup (Recommended if you have conflicts)

**Windows:**
```powershell
cd C:\Users\Asus\Software-Engineering-1404-01_G1\team9
.\reset_database.bat
```

**Linux/Mac:**
```bash
cd /path/to/Software-Engineering-1404-01_G1/team9
chmod +x reset_database.sh
./reset_database.sh
```

### Option 2: Setup Without Reset (If no conflicts)

```bash
cd C:\Users\Asus\Software-Engineering-1404-01_G1\team9
python setup_and_seed.py
```

### Expected Output

```
================================================================================
           TEAM9 VOCABULARY APP - DATABASE SETUP & SEED SCRIPT
================================================================================

Starting comprehensive database synchronization...

================================================================================
                         DISCOVERING ALL MODELS
--------------------------------------------------------------------------------

Total models discovered: 9

  • auth.Permission → Table: auth_permission
  • auth.Group → Table: auth_group
  • contenttypes.ContentType → Table: django_content_type
  • sessions.Session → Table: django_session
  • admin.LogEntry → Table: django_admin_log
  • vocabulary_app.Lesson → Table: vocabulary_app_lesson
  • vocabulary_app.Word → Table: vocabulary_app_word

...

✓ SETUP COMPLETE!
```

---

## Manual Step-by-Step Guide

If you prefer manual control or want to understand each step:

### Step 1: Check Current State

```bash
cd C:\Users\Asus\Software-Engineering-1404-01_G1\team9

# Check which migrations exist
python manage.py showmigrations

# Check if models are properly configured
python manage.py check
```

### Step 2: Identify Missing Tables

```bash
# Open Django shell
python manage.py shell

# Run this to check all models
from django.apps import apps
for model in apps.get_models():
    print(f"{model._meta.app_label}.{model._meta.object_name} → {model._meta.db_table}")
```

### Step 3: Create Migrations (if needed)

```bash
# Create migrations for all apps
python manage.py makemigrations

# Verify what will be created
python manage.py showmigrations
```

### Step 4: Apply Migrations

```bash
# Apply all pending migrations
python manage.py migrate

# Use --run-syncdb to force table creation
python manage.py migrate --run-syncdb
```

### Step 5: Create Superuser

```bash
# Interactive method
python manage.py createsuperuser

# Non-interactive (for scripts)
python manage.py createsuperuser \
    --username admin \
    --email admin@team9.com \
    --noinput

# Then set password
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='admin')
>>> user.set_password('admin123')
>>> user.save()
```

### Step 6: Run Setup Script

```bash
# Run the comprehensive setup and seed script
python setup_and_seed.py
```

---

## Conflict Resolution

### Scenario 1: Migration Conflicts Between Team Members

**Symptoms:**
- Error: "Conflicting migrations detected"
- Migration files have different numbers/names

**Solution:**

```bash
cd C:\Users\Asus\Software-Engineering-1404-01_G1\team9

# 1. Backup your database
copy db.sqlite3 db.sqlite3.backup

# 2. Remove conflicting migrations (keep __init__.py)
del vocabulary_app\migrations\0*.py

# 3. Create fresh migrations
python manage.py makemigrations

# 4. Apply migrations
python manage.py migrate

# 5. Run setup script
python setup_and_seed.py
```

### Scenario 2: Table Already Exists Error

**Symptoms:**
- Error: "table already exists"

**Solution:**

```bash
# Use fake migrations to sync Django state with database
python manage.py migrate --fake vocabulary_app zero
python manage.py migrate vocabulary_app
```

### Scenario 3: Completely Corrupted Database

**Symptoms:**
- Multiple errors
- Inconsistent state

**Solution:**

Use the reset script (recommended):

```bash
# Windows
.\reset_database.bat

# Linux/Mac
./reset_database.sh
```

---

## Troubleshooting

### Issue: "No module named 'vocabulary_app'"

**Cause:** Wrong directory or settings not configured

**Solution:**
```bash
# Make sure you're in the team9 directory
cd C:\Users\Asus\Software-Engineering-1404-01_G1\team9

# Verify DJANGO_SETTINGS_MODULE
echo %DJANGO_SETTINGS_MODULE%  # Should show: core_config.settings
```

### Issue: "CSRF verification failed"

**Cause:** CORS not properly configured

**Solution:**
Already fixed in your settings.py. Ensure you have:
```python
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite dev server
    'http://127.0.0.1:5173',
]
```

### Issue: "Cannot find User model"

**Cause:** Using default Django user instead of custom User model

**Solution:**
The script uses `get_user_model()` which automatically detects the correct user model. If you see this error, check your settings.py:
```python
AUTH_USER_MODEL = 'core.User'  # Should point to core app's User model
```

### Issue: "Permission denied" on Linux/Mac

**Cause:** Script not executable

**Solution:**
```bash
chmod +x reset_database.sh
chmod +x setup_and_seed.py
```

---

## Files Created

### 1. `setup_and_seed.py`

**Location:** `team9/setup_and_seed.py`

**Purpose:** Comprehensive database setup and seeding

**Features:**
- Dynamic model discovery using `apps.get_models()`
- Table existence verification
- Automated migration execution
- Superuser creation with default credentials
- Realistic test data generation
- Progress tracking and summary

**Usage:**
```bash
python setup_and_seed.py
```

### 2. `reset_database.bat`

**Location:** `team9/reset_database.bat`

**Purpose:** Windows batch script for complete database reset

**What it does:**
1. Backs up existing database with timestamp
2. Removes old migration files
3. Deletes database files
4. Creates fresh migrations
5. Applies migrations
6. Runs setup and seed script

**Usage:**
```bash
.\reset_database.bat
```

### 3. `reset_database.sh`

**Location:** `team9/reset_database.sh`

**Purpose:** Linux/Mac shell script for complete database reset

**What it does:**
- Same as .bat file but for Unix systems

**Usage:**
```bash
chmod +x reset_database.sh
./reset_database.sh
```

---

## Test Data Overview

### Superuser Credentials

- **Username:** admin
- **Email:** admin@team9.com
- **Password:** admin123
- **Access:** http://127.0.0.1:8000/admin/

### Seeded Lessons (5 total)

1. **General English Vocabulary** - 12 words
   - Everyday words for beginners
   - Mixed learning progress

2. **Technical Computer Terms** - 12 words
   - Programming and IT terminology
   - Various completion levels

3. **Business English** - 10 words
   - Professional workplace vocabulary
   - Different review statuses

4. **Travel and Tourism** - 10 words
   - Travel phrases and words
   - Realistic progress tracking

5. **Academic Writing** - 10 words
   - Advanced academic vocabulary
   - Spaced repetition patterns

### Word Learning States

The seeded data includes words in various states:
- **Not started**: `review_history = "00000000"`
- **In progress**: Various patterns like `"11100000"`, `"11210000"`
- **Learned**: At least 6 green ticks (e.g., `"11111100"`)
- **Complete**: All 8 days reviewed (`"11111111"`)

This ensures your frontend displays:
- ✅ Empty progress bars
- ✅ Partial progress bars
- ✅ Complete progress bars
- ✅ Realistic word review flows

---

## Verification Steps

After running the setup, verify everything works:

### 1. Check Database Tables

```bash
python manage.py dbshell
.tables  # SQLite command
.exit
```

Expected tables:
- `vocabulary_app_lesson`
- `vocabulary_app_word`
- `auth_user`
- Django built-in tables

### 2. Verify Superuser

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(is_superuser=True).count()
1  # Should show at least 1
```

### 3. Check Seeded Data

```bash
python manage.py shell
>>> from vocabulary_app.models import Lesson, Word
>>> Lesson.objects.count()
5  # Should show 5 lessons
>>> Word.objects.count()
54  # Should show 54 words
```

### 4. Test Admin Panel

1. Start server: `python manage.py runserver`
2. Navigate to: http://127.0.0.1:8000/admin/
3. Login with: admin / admin123
4. Verify you can see Lessons and Words

### 5. Test API Endpoints

```bash
# Test lessons endpoint
curl http://127.0.0.1:8000/team9/api/lessons/

# Test words endpoint
curl http://127.0.0.1:8000/team9/api/words/
```

### 6. Test Frontend

1. Start Django: `python manage.py runserver`
2. Start Vite: `cd frontend && npm run dev`
3. Open: http://localhost:5173
4. Verify:
   - ✅ Lessons display with progress bars
   - ✅ Words show correct counts
   - ✅ Progress percentages are accurate
   - ✅ Can create/delete lessons and words

---

## Advanced Usage

### Custom User ID

By default, the script uses `user_id=1`. To use a different user:

```python
# Edit setup_and_seed.py
# Find this line:
lessons = seed_lessons(user_id=1)

# Change to your preferred user ID:
lessons = seed_lessons(user_id=YOUR_USER_ID)
```

### Add More Test Data

Edit the `seed_words()` function in `setup_and_seed.py`:

```python
words_by_lesson = {
    "Your Lesson Title": [
        ("English Word", "Persian Translation"),
        # Add more words here
    ],
    # Add more lessons here
}
```

### Skip Seeding (Migrations Only)

If you only want to sync tables without test data:

```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

---

## Integration with Team Workflow

### Before Pulling Team Changes

```bash
# 1. Backup your current work
copy db.sqlite3 db.sqlite3.mywork.bak

# 2. Pull changes
git pull origin main

# 3. Reset and resync
.\reset_database.bat
```

### Before Pushing to Team

```bash
# 1. Ensure migrations are committed
git add vocabulary_app/migrations/
git commit -m "Add database migrations"

# 2. Document any model changes in commit message
```

### For New Team Members

New team members should run:

```bash
# 1. Clone repository
git clone <repo-url>

# 2. Setup environment
cd team9
pip install -r requirements.txt

# 3. Run setup script
python setup_and_seed.py

# 4. Start server
python manage.py runserver
```

---

## Summary

This comprehensive solution provides:

1. ✅ **Automated Discovery**: Uses `apps.get_models()` to find all models
2. ✅ **Complete Sync**: Creates all tables across the entire project
3. ✅ **Superuser Ready**: Admin panel access immediately
4. ✅ **Realistic Data**: Frontend displays complete state
5. ✅ **Conflict Resolution**: Reset scripts for clean slate
6. ✅ **Cross-Platform**: Works on Windows, Linux, and Mac
7. ✅ **English Comments**: All code follows project standards
8. ✅ **No New Folders**: Uses existing structure

**Next Steps:**

1. Run the setup script: `python setup_and_seed.py`
2. Start Django server: `python manage.py runserver`
3. Access admin: http://127.0.0.1:8000/admin/ (login: admin / admin123)
4. Start frontend: `cd frontend && npm run dev`
5. View frontend: http://localhost:5173

**Support:**

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review error messages carefully
3. Ensure you're in the correct directory
4. Verify Python environment is activated
5. Check that all dependencies are installed

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-05  
**Status:** Production Ready ✓
