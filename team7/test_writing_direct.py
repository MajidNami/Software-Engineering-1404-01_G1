#!/usr/bin/env python
"""
Direct test script for writing evaluation API.
Tests the full stack including authentication and API calls.
"""

import os
import sys
import django
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

from team7.models import Question
from team7.services import EvaluationService
import uuid

def test_writing_api():
    """Test the writing evaluation service directly."""
    
    print("=" * 80)
    print("Team 7 - Writing Evaluation Direct Test")
    print("=" * 80)
    
    # Get a sample question
    question = Question.objects.using('team7').filter(
        task_type='writing',
        mode='independent'
    ).first()
    
    if not question:
        print("❌ No writing questions found in database!")
        print("   Please run migrations and seed the database first.")
        return False
    
    print(f"\n✓ Found question: {question.question_id}")
    print(f"  Prompt: {question.prompt_text[:100]}...")
    
    # Sample essay text (150+ words to meet minimum requirement)
    sample_essay = """
    Technology has fundamentally transformed how we live, work, and communicate, making the world 
    a significantly better place. I strongly agree with this statement for several compelling reasons.
    
    First and foremost, technology has revolutionized communication, breaking down geographical 
    barriers that once separated people. Through email, video conferencing, and social media platforms, 
    individuals can now connect instantly with friends, family, and colleagues across the globe. This 
    unprecedented connectivity has strengthened relationships, facilitated international collaboration, 
    and created new opportunities for cross-cultural understanding.
    
    Moreover, technological advances in healthcare have dramatically improved quality of life and 
    extended human longevity. Modern diagnostic tools like MRI machines and CT scanners enable doctors 
    to detect diseases in their early stages. Electronic health records streamline patient care, while 
    telemedicine platforms make healthcare accessible to people in remote areas who previously had 
    limited access to medical services.
    
    Finally, technology has democratized education through online learning platforms, educational apps, 
    and digital resources. Students worldwide can now access high-quality educational content regardless 
    of their geographic location or economic status. This has opened up unprecedented opportunities for 
    personal and professional development.
    
    In conclusion, while technology certainly has some drawbacks, its positive impacts on communication, 
    healthcare, and education have undeniably made our world a better place to live. These benefits far 
    outweigh any negative consequences.
    """
    
    word_count = len(sample_essay.split())
    print(f"\n✓ Essay prepared: {word_count} words")
    
    # Test the evaluation service
    print("\n" + "=" * 80)
    print("Testing Evaluation Service...")
    print("=" * 80)
    
    try:
        print("\n⏳ Calling EvaluationService.evaluate_writing()...")
        service = EvaluationService()
        result, status_code = service.evaluate_writing(
            user_id=str(uuid.uuid4()),  # Generate fake user ID for testing
            question_id=str(question.question_id),
            text=sample_essay
        )
        
        print(f"\n✓ API call completed! Status code: {status_code}")
        
        if status_code == 200:
            print("\n" + "=" * 80)
            print("✅ SUCCESS - Evaluation Completed")
            print("=" * 80)
            print(f"\n📊 Overall Score: {result.get('overall_score')}/5.0")
            print(f"\n💬 Feedback:\n{result.get('feedback')}")
            
            if result.get('criteria'):
                print("\n📋 Detailed Scores:")
                for criterion in result['criteria']:
                    print(f"   • {criterion['name']}: {criterion['score']}/5.0")
                    if criterion.get('comment'):
                        print(f"     → {criterion['comment'][:100]}...")
            
            print("\n" + "=" * 80)
            return True
        else:
            print(f"\n❌ FAILED - Status code: {status_code}")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Message: {result.get('message', 'No message provided')}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION OCCURRED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_writing_api()
    sys.exit(0 if success else 1)
