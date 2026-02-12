"""
Simple script to seed test data for team9 app
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

from team9.models import Lesson, Word
from datetime import date, timedelta

# Clear existing data
Lesson.objects.using('team9').all().delete()
print("Cleared existing data")

# Create lessons
lessons_data = [
    {'title': 'General English Vocabulary', 'description': 'Essential everyday words', 'user_id': 1},
    {'title': 'Technical Computer Terms', 'description': 'Programming and IT terminology', 'user_id': 1},
    {'title': 'Business English', 'description': 'Professional vocabulary', 'user_id': 1},
]

lessons = []
for data in lessons_data:
    lesson = Lesson(**data)
    lesson.save(using='team9')
    lessons.append(lesson)
    print(f"Created lesson: {lesson.title}")

# Create words for first lesson
lesson1 = lessons[0]
words_data = [
    {'term': 'Book', 'definition': 'کتاب', 'current_day': 0, 'next_review_date': date.today()},
    {'term': 'School', 'definition': 'مدرسه', 'current_day': 1, 'next_review_date': date.today() + timedelta(days=1)},
    {'term': 'Friend', 'definition': 'دوست', 'current_day': 2, 'next_review_date': date.today() + timedelta(days=2)},
    {'term': 'Home', 'definition': 'خانه', 'current_day': 0, 'next_review_date': date.today()},
]

for data in words_data:
    word = Word(lesson=lesson1, **data)
    word.save(using='team9')
    print(f"Created word: {word.term}")

# Create words for second lesson
lesson2 = lessons[1]
tech_words = [
    {'term': 'Database', 'definition': 'پایگاه داده', 'current_day': 0, 'next_review_date': date.today()},
    {'term': 'Server', 'definition': 'سرور', 'current_day': 1, 'next_review_date': date.today() + timedelta(days=1)},
    {'term': 'API', 'definition': 'رابط برنامه‌نویسی', 'current_day': 0, 'next_review_date': date.today()},
]

for data in tech_words:
    word = Word(lesson=lesson2, **data)
    word.save(using='team9')
    print(f"Created word: {word.term}")

print(f"\n✓ Successfully created:")
print(f"  - {Lesson.objects.using('team9').count()} lessons")
print(f"  - {Word.objects.using('team9').count()} words")
