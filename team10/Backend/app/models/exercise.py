"""Exercise (Listening Item) database model and related entities."""
from typing import Optional, List, Dict, Any
from datetime import datetime
import pyodbc


class ListeningItem:
    """Represents a listening exercise item."""
    
    def __init__(
        self,
        item_id: int,
        audio_url: str,
        audio_format: str,
        audio_duration: int,
        transcript: str,
        language_code: str = "en-US",
        accent: Optional[str] = None,
        metadata: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """Initialize listening item instance."""
        self.item_id = item_id
        self.audio_url = audio_url
        self.audio_format = audio_format
        self.audio_duration = audio_duration
        self.transcript = transcript
        self.language_code = language_code
        self.accent = accent
        self.metadata = metadata
        self.created_at = created_at
        self.topics: List[str] = []
        self.questions: List['Question'] = []
    
    @staticmethod
    def from_db_row(row: pyodbc.Row) -> 'ListeningItem':
        """Create ListeningItem instance from database row."""
        return ListeningItem(
            item_id=row.item_id,
            audio_url=row.audio_url,
            audio_format=row.audio_format,
            audio_duration=row.audio_duration,
            transcript=row.transcript,
            language_code=row.language_code,
            accent=row.accent,
            metadata=row.metadata,
            created_at=row.created_at
        )


class Question:
    """Represents a listening question."""
    
    def __init__(
        self,
        question_id: int,
        item_id: int,
        skill_id: int,
        question_text: str,
        options: str,
        correct_answer: str,
        explanation: Optional[str] = None,
        order_index: int = 1,
        skill_name: Optional[str] = None
    ):
        """Initialize question instance."""
        self.question_id = question_id
        self.item_id = item_id
        self.skill_id = skill_id
        self.question_text = question_text
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation
        self.order_index = order_index
        self.skill_name = skill_name
    
    @staticmethod
    def from_db_row(row: pyodbc.Row) -> 'Question':
        """Create Question instance from database row."""
        return Question(
            question_id=row.question_id,
            item_id=row.item_id,
            skill_id=row.skill_id,
            question_text=row.question_text,
            options=row.options,
            correct_answer=row.correct_answer,
            explanation=row.explanation if hasattr(row, 'explanation') else None,
            order_index=row.order_index,
            skill_name=row.skill_name if hasattr(row, 'skill_name') else None
        )


class AssessmentAttempt:
    """Represents an assessment attempt."""
    
    def __init__(
        self,
        attempt_id: Optional[int] = None,
        user_id: Optional[int] = None,
        blueprint_id: int = 1,
        attempt_mode: str = "practice",
        status: str = "in_progress",
        raw_score: Optional[int] = None,
        scaled_score: Optional[int] = None,
        start_time: Optional[datetime] = None
    ):
        """Initialize assessment attempt instance."""
        self.attempt_id = attempt_id
        self.user_id = user_id
        self.blueprint_id = blueprint_id
        self.attempt_mode = attempt_mode
        self.status = status
        self.raw_score = raw_score
        self.scaled_score = scaled_score
        self.start_time = start_time
