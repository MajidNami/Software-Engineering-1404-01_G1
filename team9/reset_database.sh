# ============================================================================
# Team9 Database Reset and Synchronization Script for Linux/Mac
# 
# This script provides a clean slate for database synchronization by:
# 1. Backing up existing database
# 2. Removing old migration conflicts
# 3. Recreating migrations from scratch
# 4. Running the setup and seed script
#
# Author: Senior Django Architect
# Date: 2026-02-05
# Language: English (as per project standards)
# ============================================================================

#!/bin/bash

echo ""
echo "================================================================================"
echo " TEAM9 VOCABULARY APP - DATABASE RESET AND SYNC TOOL"
echo "================================================================================"
echo ""

# Get script directory and change to it
cd "$(dirname "$0")"

echo "Step 1: Backing up existing database..."
echo "--------------------------------------------------------------------------------"
if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "db.sqlite3.backup.$(date +%Y%m%d_%H%M%S).bak"
    echo "[OK] Database backed up successfully"
else
    echo "[INFO] No existing database found"
fi
echo ""

echo "Step 2: Cleaning old migration files (except __init__.py)..."
echo "--------------------------------------------------------------------------------"
if ls vocabulary_app/migrations/0*.py 1> /dev/null 2>&1; then
    rm vocabulary_app/migrations/0*.py
    echo "[OK] Old migration files removed"
else
    echo "[INFO] No old migration files to remove"
fi
echo ""

echo "Step 3: Removing database file..."
echo "--------------------------------------------------------------------------------"
if [ -f "db.sqlite3" ]; then
    rm db.sqlite3
    echo "[OK] Database file removed"
else
    echo "[INFO] No database file to remove"
fi

if [ -f "team9.sqlite3" ]; then
    rm team9.sqlite3
    echo "[OK] Team9 database file removed"
fi
echo ""

echo "Step 4: Creating fresh migrations..."
echo "--------------------------------------------------------------------------------"
python manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create migrations"
    exit 1
fi
echo "[OK] Migrations created successfully"
echo ""

echo "Step 5: Applying migrations to database..."
echo "--------------------------------------------------------------------------------"
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to apply migrations"
    exit 1
fi
echo "[OK] Migrations applied successfully"
echo ""

echo "Step 6: Running setup and seed script..."
echo "--------------------------------------------------------------------------------"
python setup_and_seed.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Setup and seed script failed"
    exit 1
fi
echo ""

echo "================================================================================"
echo " SUCCESS! Database reset and synchronization complete"
echo "================================================================================"
echo ""
echo "Your database is now clean and fully synchronized with test data."
echo ""
echo "Next steps:"
echo "  1. Start Django server: python manage.py runserver"
echo "  2. Access admin panel: http://127.0.0.1:8000/admin/"
echo "  3. Login: admin@team9.com / admin123"
echo "  4. Start frontend: cd frontend && npm run dev"
echo ""
echo "================================================================================"
echo ""
