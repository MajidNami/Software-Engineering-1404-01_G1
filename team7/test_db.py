#!/usr/bin/env python
"""Test script to verify team7 database setup."""
import os
import sys
import django

# Setup Django - ensure we're using the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

from team7.models import Question, Evaluation, DetailedScore

def main():
    print("=" * 60)
    print("Team 7 Database Verification")
    print("=" * 60)
    
    # Check Questions
    question_count = Question.objects.using('team7').count()
    print(f"\n✓ Total TOEFL Questions: {question_count}")
    
    if question_count > 0:
        print("\n Sample Questions:")
        print("-" * 60)
        for q in Question.objects.using('team7')[:3]:
            print(f"\nTask: {q.get_task_type_display()}")
            print(f"Mode: {q.mode}")
            print(f"Difficulty: {q.difficulty}/5")
            print(f"Prompt: {q.prompt_text[:100]}...")
    
    # Check Evaluations
    eval_count = Evaluation.objects.using('team7').count()
    print(f"\n✓ Total Evaluations: {eval_count}")
    
    # Check DetailedScores
    score_count = DetailedScore.objects.using('team7').count()
    print(f"✓ Total Detailed Scores: {score_count}")
    
    print("\n" + "=" * 60)
    print(" Database verification complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
