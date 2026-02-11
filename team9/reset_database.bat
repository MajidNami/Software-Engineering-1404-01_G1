@echo off
REM ============================================================================
REM Team9 Database Reset and Synchronization Script for Windows
REM 
REM This script provides a clean slate for database synchronization by:
REM 1. Backing up existing database
REM 2. Removing old migration conflicts
REM 3. Recreating migrations from scratch
REM 4. Running the setup and seed script
REM
REM Author: Senior Django Architect
REM Date: 2026-02-05
REM Language: English (as per project standards)
REM ============================================================================

echo.
echo ================================================================================
echo  TEAM9 VOCABULARY APP - DATABASE RESET AND SYNC TOOL
echo ================================================================================
echo.

REM Change to team9 directory
cd /d "%~dp0"

echo Step 1: Backing up existing database...
echo --------------------------------------------------------------------------------
if exist db.sqlite3 (
    copy db.sqlite3 db.sqlite3.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.bak
    echo [OK] Database backed up successfully
) else (
    echo [INFO] No existing database found
)
echo.

echo Step 2: Cleaning old migration files (except __init__.py)...
echo --------------------------------------------------------------------------------
if exist vocabulary_app\migrations\0*.py (
    del /q vocabulary_app\migrations\0*.py
    echo [OK] Old migration files removed
) else (
    echo [INFO] No old migration files to remove
)
echo.

echo Step 3: Removing database file...
echo --------------------------------------------------------------------------------
if exist db.sqlite3 (
    del /q db.sqlite3
    echo [OK] Database file removed
) else (
    echo [INFO] No database file to remove
)

if exist team9.sqlite3 (
    del /q team9.sqlite3
    echo [OK] Team9 database file removed
)
echo.

echo Step 4: Creating fresh migrations...
echo --------------------------------------------------------------------------------
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create migrations
    pause
    exit /b %errorlevel%
)
echo [OK] Migrations created successfully
echo.

echo Step 5: Applying migrations to database...
echo --------------------------------------------------------------------------------
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to apply migrations
    pause
    exit /b %errorlevel%
)
echo [OK] Migrations applied successfully
echo.

echo Step 6: Running setup and seed script...
echo --------------------------------------------------------------------------------
python setup_and_seed.py
if %errorlevel% neq 0 (
    echo [ERROR] Setup and seed script failed
    pause
    exit /b %errorlevel%
)
echo.

echo ================================================================================
echo  SUCCESS! Database reset and synchronization complete
echo ================================================================================
echo.
echo Your database is now clean and fully synchronized with test data.
echo.
echo Next steps:
echo   1. Start Django server: python manage.py runserver
echo   2. Access admin panel: http://127.0.0.1:8000/admin/
echo   3. Login: admin@team9.com / admin123
echo   4. Start frontend: cd frontend ^&^& npm run dev
echo.
echo ================================================================================
echo.
pause
