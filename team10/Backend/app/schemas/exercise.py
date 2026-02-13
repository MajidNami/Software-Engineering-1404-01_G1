"""Exercise-related Pydantic schemas for request/response validation."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class QuestionResponse(BaseModel):
    """Schema for a single question response."""
    question_id: int
    question_text: str
    options: str
    skill_name: str
    order_index: int
    explanation: Optional[str] = None


class ListeningItemResponse(BaseModel):
    """Schema for listening item with questions."""
    item_id: int
    audio_url: str
    audio_format: str
    audio_duration: int
    transcript: str
    language_code: str
    accent: Optional[str] = None
    topics: List[str] = []
    questions: List[QuestionResponse] = []


class ExerciseListResponse(BaseModel):
    """Schema for list of exercises."""
    exercises: List[ListeningItemResponse]
    total_count: int


class AnswerSubmission(BaseModel):
    """Schema for a single answer submission."""
    questionId: str
    answer: str


class ExerciseSubmitRequest(BaseModel):
    """Schema for exercise submission request."""
    exerciseId: str
    answers: List[AnswerSubmission]


class QuestionResult(BaseModel):
    """Schema for individual question result."""
    question_id: int
    selected_answer: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None


class SkillResult(BaseModel):
    """Schema for skill-based results."""
    skill_name: str
    correct_count: int
    total_count: int
    percentage: float


class ExerciseSubmitResponse(BaseModel):
    """Schema for exercise submission response."""
    attempt_id: int
    raw_score: int
    total_questions: int
    percentage: float
    results: List[QuestionResult]
    skill_results: List[SkillResult]
    feedback: str


class CompletedExerciseResponse(BaseModel):
    """Schema for completed exercise information."""
    exercise_id: int
    title: str
    completed_at: datetime
    score: int
    percentage: float


class ExerciseResultRequest(BaseModel):
    """Schema for posting exercise results."""
    score: int
    feedback: str


class CommentRequest(BaseModel):
    """Schema for posting a comment."""
    content: str
    userId: str


class ReviewRequest(BaseModel):
    """Schema for posting a review."""
    rating: int = Field(..., ge=1, le=5)
    content: str
    userId: str


class ReviewResponse(BaseModel):
    """Schema for review data."""
    review_id: int
    rating: int
    content: str
    user_name: str
    created_at: datetime
