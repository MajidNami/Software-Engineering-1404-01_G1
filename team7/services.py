import json
import logging
import uuid
from django.utils import timezone
from .models import Evaluation, DetailedScore, Question
from .scoring_engine.api import score_essay

logger = logging.getLogger(__name__)


class WritingEvaluator:
    """Service layer: Writing evaluation logic (FR-WR).
    
    Validates text and sends to LLM for TOEFL Writing analysis.
    Returns structured JSON per ETS rubric standards.
    """

    RUBRIC_VERSION = "ETS_iBT_2024_v1"
    MIN_WORDS = 50
    MAX_WORDS = 1000

    def __init__(self):
        pass

    def validate_length(self, text):
        """Validate word count per SRS FR-WR-01.
        
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        word_count = len(text.split())
        if word_count < self.MIN_WORDS:
            return False, f"INVALID_INPUT: Text is too short (minimum {self.MIN_WORDS} words)."
        if word_count > self.MAX_WORDS:
            return False, f"INVALID_INPUT: Text is too long (maximum {self.MAX_WORDS} words)."
        return True, "OK"

    def analyze(self, text, question_obj, mode="independent"):
        try:
            band_score = score_essay(
                essay=text,
                question=question_obj.prompt_text
            )

            return {
                "overall_score": band_score,
                "feedback": "Automated TOEFL evaluation completed.",
                "criteria": [
                    {
                        "name": "Overall",
                        "score": band_score,
                        "comment": "AI generated score"
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Scoring engine error: {str(e)}")
            return None


class EvaluationService:
    """Orchestrator for evaluation workflows (SDD Layer 2).
    
    Coordinates validation, AI analysis, and persistence.
    Implements error codes per SRS Appendix B.
    """

    def __init__(self):
        self.writing_evaluator = WritingEvaluator()

    def evaluate_writing(self, user_id, question_id, text):
        """End-to-end writing evaluation workflow (UC-01).
        
        Args:
            user_id: UUID of student
            question_id: UUID of question
            text: Submitted essay text
            
        Returns:
            tuple: (response_dict, http_status_code)
        """
        # 1. Fetch Question
        try:
            question = Question.objects.get(question_id=question_id)
        except Question.DoesNotExist:
            logger.warning(f"Question not found: {question_id}")
            return {"error": "QUESTION_NOT_FOUND", "message": "Invalid question ID"}, 404

        # 2. Input Validation (FR-WR-01)
        is_valid, message = self.writing_evaluator.validate_length(text)
        if not is_valid:
            logger.warning(f"WritingEvaluation validation failed for user {user_id}: {message}")
            return {"error": message, "code": "INVALID_INPUT"}, 400

        # 3. AI Analysis
        result = self.writing_evaluator.analyze(
            text, question, mode=question.mode
        )
        if not result:
            logger.error(f"WritingEvaluator.analyze returned None for user {user_id}")
            return {
                "error": "SERVICE_UNAVAILABLE",
                "message": "AI service temporarily unavailable. Try again later."
            }, 503

        # 4. Data Persistence (Layer 3)
        try:
            eval_obj = Evaluation.objects.create(
                user_id=user_id,
                question=question,
                task_type="writing",
                submitted_text=text,
                overall_score=result.get('overall_score'),
                ai_feedback=result.get('feedback'),
                rubric_version_id=WritingEvaluator.RUBRIC_VERSION
            )

            # Save detailed criterion scores
            for crit in result.get('criteria', []):
                DetailedScore.objects.create(
                    evaluation=eval_obj,
                    criterion=crit.get('name'),
                    score_value=crit.get('score'),
                    comment=crit.get('comment')
                )

            logger.info(f"Evaluation created: {eval_obj.evaluation_id} for user {user_id}")

            # 5. Response (FR-API-02)
            return {
                "status": "success",
                "evaluation_id": str(eval_obj.evaluation_id),
                "overall_score": float(eval_obj.overall_score) if eval_obj.overall_score else None,
                "feedback": eval_obj.ai_feedback,
                "criteria": [
                    {
                        "name": ds.criterion,
                        "score": float(ds.score_value),
                        "comment": ds.comment
                    }
                    for ds in eval_obj.detailed_scores.all()
                ],
                "created_at": eval_obj.created_at.isoformat()
            }, 200

        except Exception as e:
            logger.exception(f"Error saving evaluation for user {user_id}: {str(e)}")
            return {
                "error": "INTERNAL_ERROR",
                "message": "Failed to save evaluation."
            }, 500

    def get_user_history(self, user_id, limit=50):
        """Fetch evaluation history for student (UC-03).
        
        Args:
            user_id: UUID of student
            limit: Max records to return
            
        Returns:
            tuple: (response_dict, http_status_code)
        """
        try:
            evaluations = Evaluation.objects.filter(
                user_id=user_id
            ).select_related('question').prefetch_related('detailed_scores').order_by('-created_at')[:limit]

            if not evaluations.exists():
                logger.info(f"No evaluations found for user {user_id}")
                return {
                    "status": "no_data",
                    "message": "No attempts yet. Start a practice test!",
                    "attempts": []
                }, 200

            attempts = []
            for eval_obj in evaluations:
                attempts.append({
                    "evaluation_id": str(eval_obj.evaluation_id),
                    "task_type": eval_obj.task_type,
                    "question_id": str(eval_obj.question.question_id),
                    "overall_score": float(eval_obj.overall_score) if eval_obj.overall_score else None,
                    "created_at": eval_obj.created_at.isoformat(),
                    "criteria": [
                        {
                            "name": ds.criterion,
                            "score": float(ds.score_value)
                        }
                        for ds in eval_obj.detailed_scores.all()
                    ]
                })

            return {
                "status": "success",
                "total_attempts": len(attempts),
                "attempts": attempts
            }, 200

        except Exception as e:
            logger.exception(f"Error fetching history for user {user_id}: {str(e)}")
            return {
                "error": "INTERNAL_ERROR",
                "message": "Failed to retrieve history."
            }, 500