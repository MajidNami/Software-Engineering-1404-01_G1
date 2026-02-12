#!/usr/bin/env python
"""
Comprehensive Database Setup and Seeding Script for Team9 Vocabulary App

This script:
1. Discovers all registered models dynamically using apps.get_models()
2. Creates database tables for all models
3. Creates a superuser for the admin panel
4. Populates all necessary tables with realistic test data

Usage:
    python setup_and_seed.py

Requirements:
    - Django project must be properly configured
    - Virtual environment should be activated (if used)
    - Database connection should be configured in settings.py

Author: Senior Django Architect
Date: 2026-02-05
Language: English (as per project standards)
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

from django.core.management import call_command
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import connection
from team9.models import Lesson, Word


def print_banner(text, char="="):
    """Print a formatted banner for better console output readability"""
    width = 80
    print("\n" + char * width)
    print(f"{text:^{width}}")
    print(char * width + "\n")


def discover_all_models():
    """
    Dynamically discover all Django models in the project.
    
    Returns:
        list: List of all model classes registered in INSTALLED_APPS
    """
    print_banner("DISCOVERING ALL MODELS", "-")
    
    all_models = apps.get_models()
    
    print(f"Total models discovered: {len(all_models)}\n")
    
    for model in all_models:
        app_label = model._meta.app_label
        model_name = model._meta.object_name
        table_name = model._meta.db_table
        print(f"  • {app_label}.{model_name} → Table: {table_name}")
    
    return all_models


def check_table_exists(table_name):
    """
    Check if a table exists in the database.
    
    Args:
        table_name (str): Name of the database table
        
    Returns:
        bool: True if table exists, False otherwise
    """
    # Use Django's introspection to get all table names
    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
        return table_name in table_names


def verify_tables():
    """
    Verify that all model tables exist in the database.
    
    Returns:
        tuple: (missing_tables list, existing_tables list)
    """
    print_banner("VERIFYING DATABASE TABLES", "-")
    
    all_models = apps.get_models()
    missing_tables = []
    existing_tables = []
    
    for model in all_models:
        table_name = model._meta.db_table
        if check_table_exists(table_name):
            existing_tables.append(table_name)
            print(f"  ✓ Table '{table_name}' exists")
        else:
            missing_tables.append(table_name)
            print(f"  ✗ Table '{table_name}' is MISSING")
    
    print(f"\nSummary: {len(existing_tables)} exist, {len(missing_tables)} missing")
    
    return missing_tables, existing_tables


def run_migrations():
    """
    Run Django migrations to create all necessary database tables.
    This ensures that all models have their corresponding tables in the database.
    """
    print_banner("RUNNING MIGRATIONS")
    
    try:
        # Check for migration issues
        print("Checking for migration conflicts...")
        call_command('makemigrations', '--check', '--dry-run')
        print("  ✓ No migration conflicts detected\n")
    except SystemExit:
        print("  ! Creating new migrations...")
        call_command('makemigrations')
        print("  ✓ Migrations created\n")
    
    # Apply all migrations
    print("Applying migrations to database...")
    call_command('migrate', '--run-syncdb')
    print("  ✓ All migrations applied successfully\n")


def create_superuser():
    """
    Create a superuser for the Django admin panel if one doesn't exist.
    
    Default credentials:
        Username: admin
        Email: admin@team9.com
        Password: admin123
    
    Returns:
        User: The created or existing superuser
    """
    print_banner("CREATING SUPERUSER")
    
    User = get_user_model()
    username = "admin"
    email = "admin@team9.com"
    password = "admin123"
    
    # Check if superuser already exists
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"  ! Superuser '{username}' already exists")
        print(f"    Using existing user (ID: {user.pk})")
        return user
    
    # Create new superuser
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        # Set additional fields
        user.first_name = "Admin"
        user.last_name = "User"
        user.save()
        
        print(f"  ✓ Superuser created successfully")
        print(f"    Username: {username}")
        print(f"    Email: {email}")
        print(f"    Password: {password}")
        print(f"    User ID: {user.pk}")
        print(f"\n  → Access admin panel at: http://127.0.0.1:8000/admin/")
        return user
    except Exception as e:
        print(f"  ✗ Error creating superuser: {e}")
        import traceback
        traceback.print_exc()
        return None


def seed_lessons(user_id=1):
    """
    Create realistic lesson data for testing.
    
    Args:
        user_id (int): The user ID to associate with lessons
        
    Returns:
        list: List of created Lesson objects
    """
    print_banner("SEEDING LESSONS", "-")
    
    # Check if lessons already exist
    if Lesson.objects.filter(user_id=user_id).exists():
        print(f"  ! Lessons for user_id={user_id} already exist")
        existing_lessons = list(Lesson.objects.filter(user_id=user_id))
        print(f"    Found {len(existing_lessons)} existing lessons")
        return existing_lessons
    
    lessons_data = [
        {
            "title": "General English Vocabulary",
            "description": "Essential everyday words for beginners. Start your English learning journey here!"
        },
        {
            "title": "Technical Computer Terms",
            "description": "Programming and IT terminology for developers and tech enthusiasts."
        },
        {
            "title": "Business English",
            "description": "Professional vocabulary for workplace communication and business meetings."
        },
        {
            "title": "Travel and Tourism",
            "description": "Useful phrases and words for traveling abroad and exploring new places."
        },
        {
            "title": "Academic Writing",
            "description": "Advanced vocabulary for essays, research papers, and academic discourse."
        }
    ]
    
    created_lessons = []
    
    for lesson_data in lessons_data:
        lesson = Lesson.objects.create(
            user_id=user_id,
            title=lesson_data["title"],
            description=lesson_data["description"]
        )
        created_lessons.append(lesson)
        print(f"  ✓ Created: {lesson.title} (ID: {lesson.id})")
    
    print(f"\n  Total lessons created: {len(created_lessons)}")
    return created_lessons


def seed_words(lessons):
    """
    Create realistic word data for each lesson with various learning statuses.
    
    Args:
        lessons (list): List of Lesson objects to add words to
    """
    print_banner("SEEDING WORDS", "-")
    
    # Words database organized by lesson category
    words_by_lesson = {
        "General English Vocabulary": [
            ("Book", "کتاب"),
            ("School", "مدرسه"),
            ("Friend", "دوست"),
            ("Family", "خانواده"),
            ("Home", "خانه"),
            ("Work", "کار"),
            ("Food", "غذا"),
            ("Water", "آب"),
            ("Time", "زمان"),
            ("Day", "روز"),
            ("Night", "شب"),
            ("Morning", "صبح"),
        ],
        "Technical Computer Terms": [
            ("Database", "پایگاه داده"),
            ("Server", "سرور"),
            ("Request", "درخواست"),
            ("Response", "پاسخ"),
            ("Authentication", "احراز هویت"),
            ("Algorithm", "الگوریتم"),
            ("Variable", "متغیر"),
            ("Function", "تابع"),
            ("Array", "آرایه"),
            ("Loop", "حلقه"),
            ("API", "رابط برنامه‌نویسی"),
            ("Framework", "چارچوب"),
        ],
        "Business English": [
            ("Meeting", "جلسه"),
            ("Deadline", "مهلت"),
            ("Revenue", "درآمد"),
            ("Budget", "بودجه"),
            ("Contract", "قرارداد"),
            ("Investment", "سرمایه‌گذاری"),
            ("Stakeholder", "ذینفع"),
            ("Strategy", "استراتژی"),
            ("Profit", "سود"),
            ("Loss", "زیان"),
        ],
        "Travel and Tourism": [
            ("Airport", "فرودگاه"),
            ("Hotel", "هتل"),
            ("Passport", "گذرنامه"),
            ("Ticket", "بلیط"),
            ("Reservation", "رزرو"),
            ("Luggage", "چمدان"),
            ("Customs", "گمرک"),
            ("Currency", "ارز"),
            ("Tourist", "گردشگر"),
            ("Destination", "مقصد"),
        ],
        "Academic Writing": [
            ("Hypothesis", "فرضیه"),
            ("Methodology", "روش‌شناسی"),
            ("Analysis", "تحلیل"),
            ("Conclusion", "نتیجه‌گیری"),
            ("Evidence", "شواهد"),
            ("Citation", "استناد"),
            ("Reference", "مرجع"),
            ("Abstract", "چکیده"),
            ("Introduction", "مقدمه"),
            ("Discussion", "بحث"),
        ]
    }
    
    # Various review history patterns for realistic data
    review_patterns = [
        ("00000000", 0, False),  # Not started
        ("10000000", 1, False),  # Just started
        ("11000000", 2, False),  # Early progress
        ("11100000", 3, False),  # Making progress
        ("11110000", 4, False),  # Halfway
        ("11111000", 5, False),  # Almost learned
        ("11111100", 6, True),   # Learned (6 greens)
        ("11111110", 7, True),   # Almost complete
        ("11111111", 8, True),   # Fully complete
        ("12110000", 3, False),  # Mixed performance
        ("11210000", 3, False),  # Some mistakes
    ]
    
    total_words_created = 0
    
    for lesson in lessons:
        # Get words for this lesson category
        words_list = words_by_lesson.get(lesson.title, [])
        
        if not words_list:
            print(f"  ! No words defined for lesson: {lesson.title}")
            continue
        
        print(f"\n  Adding words to: {lesson.title}")
        
        for idx, (term, definition) in enumerate(words_list):
            # Assign different review patterns for variety
            pattern_idx = idx % len(review_patterns)
            review_history, current_day, is_learned = review_patterns[pattern_idx]
            
            # Calculate next review date based on current status
            if is_learned:
                # For learned words, set far future date (no immediate review needed)
                next_review_date = date.today() + timedelta(days=365)
                last_review_date = date.today() - timedelta(days=5)
            elif current_day == 0:
                next_review_date = date.today()  # Ready to review
                last_review_date = None
            else:
                next_review_date = date.today() + timedelta(days=current_day)
                last_review_date = date.today() - timedelta(days=1)
            
            word = Word.objects.create(
                lesson=lesson,
                term=term,
                definition=definition,
                current_day=current_day,
                review_history=review_history,
                is_learned=is_learned,
                last_review_date=last_review_date,
                next_review_date=next_review_date
            )
            
            status = "✓ Learned" if is_learned else f"Day {current_day}"
            print(f"    • {term} → {definition} [{status}]")
            total_words_created += 1
        
        # Show progress percentage for the lesson
        progress = lesson.progress_percent
        print(f"    Progress: {progress}%")
    
    print(f"\n  Total words created: {total_words_created}")


def show_summary():
    """
    Display a summary of all data in the database.
    """
    print_banner("DATABASE SUMMARY")
    
    # Count records for each model
    User = get_user_model()
    
    user_count = User.objects.count()
    lesson_count = Lesson.objects.count()
    word_count = Word.objects.count()
    learned_words = Word.objects.filter(is_learned=True).count()
    
    print(f"  Users: {user_count}")
    print(f"  Lessons: {lesson_count}")
    print(f"  Words: {word_count}")
    print(f"  Learned Words: {learned_words}")
    
    if lesson_count > 0:
        print(f"\n  Lessons breakdown:")
        for lesson in Lesson.objects.all():
            word_count_in_lesson = lesson.words.count()
            progress = lesson.progress_percent
            print(f"    • {lesson.title}: {word_count_in_lesson} words, {progress}% progress")


def main():
    """
    Main execution flow for database setup and seeding.
    """
    print_banner("TEAM9 VOCABULARY APP - DATABASE SETUP & SEED SCRIPT")
    
    print("Starting comprehensive database synchronization...\n")
    
    try:
        # Step 1: Discover all models
        all_models = discover_all_models()
        
        # Step 2: Verify existing tables
        missing_tables, existing_tables = verify_tables()
        
        # Step 3: Run migrations to create missing tables
        if missing_tables:
            print("\n⚠️  Missing tables detected. Running migrations...\n")
            run_migrations()
            print("\n✓ All tables synchronized successfully!\n")
        else:
            print("\n✓ All tables already exist!\n")
            # Still run migrations to ensure everything is up to date
            run_migrations()
        
        # Step 4: Create superuser
        superuser = create_superuser()
        
        if not superuser:
            print("\n⚠️  Could not create superuser. Exiting...")
            return
        
        # Step 5: Seed lessons
        lessons = seed_lessons(user_id=1)
        
        # Step 6: Seed words
        seed_words(lessons)
        
        # Step 7: Show summary
        show_summary()
        
        # Success message
        print_banner("✓ SETUP COMPLETE!", "=")
        print("Your database is now fully synchronized and populated with test data!")
        print("\nNext steps:")
        print("  1. Start the Django server: python manage.py runserver")
        print("  2. Access the admin panel: http://127.0.0.1:8000/admin/")
        print("  3. Login with: admin@team9.com / admin123")
        print("  4. Start the frontend: cd frontend && npm run dev")
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
