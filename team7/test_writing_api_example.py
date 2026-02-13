"""
Example script to test the Writing Evaluation API.
This demonstrates how the frontend should call the backend.

Note: This requires a valid JWT token from user login.
For testing purposes, you can use the Django shell to create a test evaluation.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
import django
django.setup()

from team7.models import Question, Evaluation
from team7.services import EvaluationService
import uuid

def test_writing_evaluation():
    """Test the writing evaluation service directly (bypasses HTTP/auth)."""
    
    print("=" * 60)
    print("Team 7 - Writing Evaluation Test")
    print("=" * 60)
    
    # Get a sample question
    question = Question.objects.using('team7').filter(
        task_type='writing',
        mode='independent'
    ).first()
    
    if not question:
        print("❌ No writing questions found in database!")
        return
    
    print(f"\n📝 Question: {question.prompt_text[:100]}...")
    
    # Sample essay text (meets minimum 50 words requirement)
    sample_essay = """
    I strongly agree that technology has made the world a better place to live. 
    First, technology has revolutionized communication, allowing people to connect 
    instantly across vast distances through email, video calls, and social media. 
    This has strengthened relationships and enabled global collaboration.
    
    Second, technology has improved healthcare dramatically. Medical devices, 
    electronic health records, and telemedicine have made healthcare more accessible 
    and effective. Modern diagnostic tools can detect diseases earlier, saving lives.
    
    Finally, technology has enhanced education through online learning platforms, 
    educational apps, and digital resources. Students worldwide can now access 
    quality education regardless of their location or economic status.
    
    In conclusion, while technology has some drawbacks, its benefits in communication, 
    healthcare, and education have undeniably made our world a better place.
    """
    
    print(f"\n📄 Essay length: {len(sample_essay.split())} words")
    
    # Test the evaluation
    print("\n🤖 Sending to AI evaluator...")
    
    try:
        service = EvaluationService()
        result = service.evaluate_writing(
            user_id=uuid.uuid4(),  # Fake user ID for testing
            question_id=str(question.question_id),
            text=sample_essay
        )
        
        print("\n Evaluation Complete!")
        print(f"\n Overall Score: {result['overall_score']}/5.0")
        print(f"\n Feedback:\n{result['ai_feedback']}")
        
        if result.get('detailed_scores'):
            print("\n Detailed Scores:")
            for score in result['detailed_scores']:
                print(f"  - {score['criterion']}: {score['score_value']}/5.0")
                if score.get('comment'):
                    print(f"    Comment: {score['comment']}")
        
        print("\n" + "=" * 60)
        print("✓Test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_writing_evaluation()
