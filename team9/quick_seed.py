#!/usr/bin/env python
"""Quick seed script for team9 database"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

from team9.models import Lesson, Word
from datetime import date

# Create lessons
print("Creating lessons...")
lessons_data = [
    {'title': 'General English Vocabulary', 'description': 'Essential everyday words', 'user_id': 1},
    {'title': 'Technical Computer Terms', 'description': 'Programming and IT terminology', 'user_id': 1},
    {'title': 'Business English', 'description': 'Professional vocabulary', 'user_id': 1},
    {'title': 'Travel and Tourism', 'description': 'Travel-related terms', 'user_id': 1},
    {'title': 'Academic Writing', 'description': 'Scholarly terms', 'user_id': 1},
]

lessons = []
for data in lessons_data:
    lesson, created = Lesson.objects.get_or_create(
        title=data['title'],
        defaults={'description': data['description'], 'user_id': data['user_id']}
    )
    lessons.append(lesson)
    status = "Created" if created else "Already exists"
    print(f"{status}: {lesson.title}")

# Create words for first lesson
print("\nCreating words...")
words_data = [
    {'term': 'accomplish', 'definition': 'انجام دادن، به پایان رساندن'},
    {'term': 'achievement', 'definition': 'دستاورد، موفقیت'},
    {'term': 'approach', 'definition': 'رویکرد، نزدیک شدن'},
    {'term': 'benefit', 'definition': 'سود، منفعت'},
    {'term': 'challenge', 'definition': 'چالش، مشکل'},
    {'term': 'contribute', 'definition': 'مشارکت کردن، کمک کردن'},
    {'term': 'develop', 'definition': 'توسعه دادن، پیشرفت کردن'},
    {'term': 'efficient', 'definition': 'کارآمد، موثر'},
    {'term': 'enhance', 'definition': 'بهبود بخشیدن، ارتقا دادن'},
    {'term': 'establish', 'definition': 'برقرار کردن، تاسیس کردن'},
    {'term': 'evaluate', 'definition': 'ارزیابی کردن'},
    {'term': 'fundamental', 'definition': 'اساسی، بنیادی'},
]

for word_data in words_data:
    word, created = Word.objects.get_or_create(
        term=word_data['term'],
        lesson=lessons[0],
        defaults={
            'definition': word_data['definition'],
            'next_review_date': date.today()
        }
    )
    status = "Created" if created else "Already exists"
    print(f"{status}: {word.term}")

print(f"\n✓ Total lessons: {Lesson.objects.count()}")
print(f"✓ Total words: {Word.objects.count()}")
