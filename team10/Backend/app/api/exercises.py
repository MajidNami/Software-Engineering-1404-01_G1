"""Exercise (Listening Items) management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import pyodbc
from app.db.database import get_db
from app.schemas.exercise import (
    ExerciseListResponse, ListeningItemResponse, QuestionResponse,
    ExerciseSubmitRequest, ExerciseSubmitResponse, QuestionResult,
    SkillResult, CompletedExerciseResponse, ExerciseResultRequest,
    CommentRequest, ReviewRequest, ReviewResponse
)
from app.schemas.base import MessageResponse
from app.services.exercise_service import exercise_service
from app.core.dependencies import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/listening", response_model=ExerciseListResponse)
async def get_listening_exercises(
    cursor: pyodbc.Cursor = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve all available listening exercises."""
    items = exercise_service.get_all_listening_items(cursor, limit=100)
    
    exercises = []
    for item in items:
        questions = [
            QuestionResponse(
                question_id=q.question_id,
                question_text=q.question_text,
                options=q.options,
                skill_name=q.skill_name or "Unknown",
                order_index=q.order_index,
                explanation=q.explanation
            )
            for q in item.questions
        ]
        
        exercises.append(ListeningItemResponse(
            item_id=item.item_id,
            audio_url=item.audio_url,
            audio_format=item.audio_format,
            audio_duration=item.audio_duration,
            transcript=item.transcript,
            language_code=item.language_code,
            accent=item.accent,
            topics=item.topics,
            questions=questions
        ))
    
    return ExerciseListResponse(
        exercises=exercises,
        total_count=len(exercises)
    )


@router.get("/{exercise_id}", response_model=ListeningItemResponse)
async def get_exercise_by_id(
    exercise_id: int,
    cursor: pyodbc.Cursor = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve a specific listening exercise by ID."""
    item = exercise_service.get_listening_item_by_id(cursor, exercise_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    questions = [
        QuestionResponse(
            question_id=q.question_id,
            question_text=q.question_text,
            options=q.options,
            skill_name=q.skill_name or "Unknown",
            order_index=q.order_index,
            explanation=q.explanation
        )
        for q in item.questions
    ]
    
    return ListeningItemResponse(
        item_id=item.item_id,
        audio_url=item.audio_url,
        audio_format=item.audio_format,
        audio_duration=item.audio_duration,
        transcript=item.transcript,
        language_code=item.language_code,
        accent=item.accent,
        topics=item.topics,
        questions=questions
    )


@router.post("/listening/submit", response_model=ExerciseSubmitResponse)
async def submit_listening_exercise(
    request: ExerciseSubmitRequest,
    cursor: pyodbc.Cursor = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit answers for a listening exercise and receive results."""
    item_id = int(request.exerciseId)
    
    item = exercise_service.get_listening_item_by_id(cursor, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    answers_dict = {
        int(ans.questionId): ans.answer 
        for ans in request.answers
    }
    
    attempt_id, results, skill_results = exercise_service.submit_exercise_answers(
        cursor=cursor,
        user_id=current_user.user_id,
        item_id=item_id,
        answers=answers_dict
    )
    
    total_questions = len(results)
    correct_count = sum(1 for r in results if r["is_correct"])
    percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    feedback = ExerciseService._generate_feedback(percentage)
    
    return ExerciseSubmitResponse(
        attempt_id=attempt_id,
        raw_score=correct_count,
        total_questions=total_questions,
        percentage=round(percentage, 2),
        results=[QuestionResult(**r) for r in results],
        skill_results=[SkillResult(**sr) for sr in skill_results],
        feedback=feedback
    )


@router.get("/{user_id}/exercises/completed", response_model=List[CompletedExerciseResponse])
async def get_completed_exercises(
    user_id: int,
    cursor: pyodbc.Cursor = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve list of completed exercises for a user."""
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's exercises"
        )
    
    completed = exercise_service.get_user_completed_exercises(cursor, user_id)
    return [CompletedExerciseResponse(**ex) for ex in completed]


@router.put("/{user_id}/exercises/{exercise_id}/complete", response_model=MessageResponse)
async def mark_exercise_complete(
    user_id: int,
    exercise_id: int,
    cursor: pyodbc.Cursor = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark an exercise as completed for a user."""
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's exercises"
        )
    
    success = exercise_service.mark_exercise_complete(cursor, user_id, exercise_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise attempt not found"
        )
    
    return MessageResponse(message="Exercise marked as complete")


@router.post("/{exercise_id}/results", response_model=MessageResponse)
async def post_exercise_results(
    exercise_id: int,
    request: ExerciseResultRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Post results for an exercise (placeholder for future implementation)."""
    return MessageResponse(
        message=f"Results posted for exercise {exercise_id}: Score {request.score}"
    )


@router.post("/{exercise_id}/comments", response_model=MessageResponse)
async def post_exercise_comment(
    exercise_id: int,
    request: CommentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Post a comment on an exercise (placeholder for future implementation)."""
    return MessageResponse(
        message=f"Comment posted on exercise {exercise_id}"
    )


@router.get("/{exercise_id}/reviews", response_model=List[ReviewResponse])
async def get_exercise_reviews(
    exercise_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Get reviews for an exercise (placeholder for future implementation)."""
    return []


@router.post("/{exercise_id}/reviews", response_model=MessageResponse)
async def post_exercise_review(
    exercise_id: int,
    request: ReviewRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Post a review for an exercise (placeholder for future implementation)."""
    return MessageResponse(
        message=f"Review posted for exercise {exercise_id} with rating {request.rating}"
    )


class ExerciseService:
    """Helper class for exercise-related utilities."""
    
    @staticmethod
    def _generate_feedback(percentage: float) -> str:
        """Generate feedback message based on score percentage."""
        if percentage >= 90:
            return "Excellent! You have a strong understanding of the material."
        elif percentage >= 75:
            return "Great job! You're doing well with most concepts."
        elif percentage >= 60:
            return "Good effort! Keep practicing to improve your skills."
        elif percentage >= 50:
            return "You're making progress. Review the material and try again."
        else:
            return "Keep practicing! Focus on understanding the key concepts."
