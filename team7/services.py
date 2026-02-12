import json
import logging
import uuid
import os
from django.conf import settings
from django.utils import timezone
from openai import OpenAI
from .models import Evaluation, DetailedScore, Question

logger = logging.getLogger(__name__)


class WritingEvaluator:
    """Service layer: Writing evaluation logic (FR-WR).
    
    Validates text and sends to LLM for TOEFL Writing analysis.
    Returns structured JSON per ETS rubric standards.
    """

    RUBRIC_VERSION = "ETS_iBT_2024_v1"
    MIN_WORDS = 50
    MAX_WORDS = 150

    def __init__(self):
        """Initialize LLM client from Django settings."""
        self.client = OpenAI(
            api_key=getattr(settings, 'AI_GENERATOR_API_KEY', 'PLACEHOLDER_KEY'),
            base_url=getattr(settings, 'AI_GENERATOR_BASE_URL', 'https://api.gpt4-all.xyz/v1')
        )
        self.model = getattr(settings, 'AI_GENERATOR_MODEL', 'gemini-3-flash-preview')

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
        """Send text to LLM and return structured JSON per ETS rubric.
        
        Args:
            text: Student essay
            question_obj: Question model instance
            mode: 'independent' or 'integrated'
            
        Returns:
            dict: Parsed JSON with overall_score, feedback, criteria OR None on failure
        """
        system_prompt = (
            "You are a strict TOEFL iBT Writing evaluator. "
            "Analyze the student's essay based on ETS official rubrics. "
            "Return ONLY a raw JSON object (no markdown, no code blocks). \n"
            "JSON SCHEMA: {\n"
            "  'overall_score': float between 0.0 and 5.0,\n"
            "  'feedback': string with overall constructive feedback,\n"
            "  'criteria': [\n"
            "    {'name': 'Grammar', 'score': float 0-5, 'comment': string},\n"
            "    {'name': 'Vocabulary', 'score': float 0-5, 'comment': string},\n"
            "    {'name': 'Organization', 'score': float 0-5, 'comment': string},\n"
            "    {'name': 'Topic Development', 'score': float 0-5, 'comment': string}\n"
            "  ]\n"
            "}\n"
            "Ensure 'feedback' includes at least ONE specific suggestion (FR-WR-05)."
        )

        user_content = (
            f"Task Mode: {mode}\n"
            f"Question: {question_obj.prompt_text}\n"
            f"\nStudent Essay:\n{text}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                stream=False,
                temperature=0.3,  # Low temperature for consistency
            )

            raw_content = response.choices[0].message.content
            clean_content = raw_content.replace("```json", "").replace("```", "").strip()
            result_json = json.loads(clean_content)

            logger.info(f"WritingEvaluator.analyze: Success. Score={result_json.get('overall_score')}")
            return result_json

        except json.JSONDecodeError as e:
            logger.error(f"WritingEvaluator JSON parse error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"WritingEvaluator LLM error: {str(e)}")
            return None


class SpeakingEvaluator:
    """Service layer: Speaking evaluation logic (FR-SP).
    
    Handles ASR transcription and LLM-based speaking assessment.
    Evaluates Delivery, Fluency, and Topic Development per ETS rubrics.
    """

    RUBRIC_VERSION = "ETS_iBT_Speaking_2024_v1"
    MIN_DURATION_SEC = 30
    MAX_DURATION_SEC = 90
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FORMATS = ['.wav', '.mp3', '.flac']

    def __init__(self):
        """Initialize OpenAI client for both ASR (Whisper) and LLM."""
        self.client = OpenAI(
            api_key=getattr(settings, 'AI_GENERATOR_API_KEY', 'PLACEHOLDER_KEY'),
            base_url=getattr(settings, 'AI_GENERATOR_BASE_URL', 'https://api.gpt4-all.xyz/v1')
        )
        self.model = getattr(settings, 'AI_GENERATOR_MODEL', 'gemini-3-flash-preview')

    def validate_audio_file(self, audio_file):
        """Validate audio file format and size per SRS FR-SP-01.
        
        Args:
            audio_file: Django UploadedFile object
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        # Check file extension
        file_ext = os.path.splitext(audio_file.name)[1].lower()
        if file_ext not in self.ALLOWED_FORMATS:
            return False, f"INVALID_INPUT: File format '{file_ext}' not supported. Use {', '.join(self.ALLOWED_FORMATS)}."
        
        # Check file size (convert to MB)
        file_size_mb = audio_file.size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"INVALID_INPUT: File size ({file_size_mb:.1f}MB) exceeds limit of {self.MAX_FILE_SIZE_MB}MB."
        
        return True, "OK"

    def transcribe_audio(self, audio_file, timeout=30):
        """Transcribe audio to text using OpenAI Whisper API (ASR).
        
        Args:
            audio_file: Django UploadedFile object or file path
            timeout: API request timeout in seconds
            
        Returns:
            dict: {'transcript': str, 'language': str} OR None on failure
        """
        try:
            logger.info(f"Starting ASR transcription for file: {audio_file.name if hasattr(audio_file, 'name') else 'unknown'}")
            
            # OpenAI Whisper API expects file-like object
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",  # Get detailed response with metadata
                language="en"  # TOEFL is English-only
            )
            
            transcript_text = response.text.strip()
            
            # Check if speech was detected (FR-SP validation)
            if not transcript_text or len(transcript_text) < 10:
                logger.warning("ASR: No speech detected or transcript too short")
                return None
            
            logger.info(f"ASR transcription successful. Length: {len(transcript_text)} chars")
            return {
                'transcript': transcript_text,
                'language': getattr(response, 'language', 'en'),
                'duration': getattr(response, 'duration', None)
            }
            
        except TimeoutError:
            logger.error(f"ASR API timeout after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"ASR transcription error: {str(e)}")
            return None

    def analyze_speaking(self, transcript_text, question_obj, mode="independent"):
        """Analyze transcript using LLM for Speaking scoring.
        
        Args:
            transcript_text: Transcribed speech text
            question_obj: Question model instance
            mode: 'independent' or 'integrated'
            
        Returns:
            dict: Parsed JSON with overall_score, feedback, criteria OR None on failure
        """
        system_prompt = (
            "You are a strict TOEFL iBT Speaking evaluator. "
            "Analyze the student's spoken response based on ETS official rubrics. "
            "Focus on: Delivery (clarity, pace, pronunciation), Language Use (grammar, vocabulary), "
            "and Topic Development (content relevance, coherence). "
            "Return ONLY a raw JSON object (no markdown, no code blocks). \n"
            "JSON SCHEMA: {\n"
            "  'overall_score': float between 0.0 and 4.0,\n"
            "  'feedback': string with overall constructive feedback,\n"
            "  'criteria': [\n"
            "    {'name': 'Delivery', 'score': float 0-4, 'comment': string},\n"
            "    {'name': 'Language Use', 'score': float 0-4, 'comment': string},\n"
            "    {'name': 'Topic Development', 'score': float 0-4, 'comment': string}\n"
            "  ]\n"
            "}\n"
            "Ensure 'feedback' includes specific suggestions for improvement."
        )

        user_content = (
            f"Task Mode: {mode}\n"
            f"Question: {question_obj.prompt_text}\n"
            f"\nStudent's Spoken Response (Transcribed):\n{transcript_text}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                stream=False,
                temperature=0.3,
            )

            raw_content = response.choices[0].message.content
            clean_content = raw_content.replace("```json", "").replace("```", "").strip()
            result_json = json.loads(clean_content)

            logger.info(f"SpeakingEvaluator.analyze: Success. Score={result_json.get('overall_score')}")
            return result_json

        except json.JSONDecodeError as e:
            logger.error(f"SpeakingEvaluator JSON parse error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"SpeakingEvaluator LLM error: {str(e)}")
            return None


class EvaluationService:
    """Orchestrator for evaluation workflows (SDD Layer 2).
    
    Coordinates validation, AI analysis, and persistence.
    Implements error codes per SRS Appendix B.
    """

    def __init__(self):
        self.writing_evaluator = WritingEvaluator()
        self.speaking_evaluator = SpeakingEvaluator()

    def evaluate_writing(self, user_id, question_id, text):
        """End-to-end writing evaluation workflow (UC-01).
        
        Args:
            user_id: UUID of student
            question_id: UUID of question
            text: Submitted essay text
            
        Returns:
            tuple: (response_dict, http_status_code)
        """
        logger.info(f"evaluate_writing called with user_id: {user_id}, question_id: {question_id}")
        
        # 1. Fetch Question
        try:
            question = Question.objects.using('team7').get(question_id=question_id)
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
            # Use explicit 'team7' database to ensure data is saved to team's database
            eval_obj = Evaluation.objects.using('team7').create(
                user_id=user_id,
                question=question,
                exam=question.exam,  # Save exam reference for history tracking
                task_type="writing",
                submitted_text=text,
                overall_score=result.get('overall_score'),
                ai_feedback=result.get('feedback'),
                rubric_version_id=WritingEvaluator.RUBRIC_VERSION
            )

            logger.info(f"Created evaluation with user_id: {eval_obj.user_id} (type: {type(eval_obj.user_id)})")
            
            # Save detailed criterion scores
            for crit in result.get('criteria', []):
                DetailedScore.objects.using('team7').create(
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

    def evaluate_speaking(self, user_id, question_id, audio_file, audio_filename=None):
        """End-to-end speaking evaluation workflow (UC-02).
        
        Args:
            user_id: UUID of student
            question_id: UUID of question
            audio_file: Django UploadedFile object
            audio_filename: Optional custom filename for storage
            
        Returns:
            tuple: (response_dict, http_status_code)
        """
        # 1. Fetch Question
        try:
            question = Question.objects.using('team7').get(question_id=question_id)
        except Question.DoesNotExist:
            logger.warning(f"Question not found: {question_id}")
            return {"error": "QUESTION_NOT_FOUND", "message": "Invalid question ID"}, 404

        # 2. Validate Audio File (FR-SP-01)
        is_valid, message = self.speaking_evaluator.validate_audio_file(audio_file)
        if not is_valid:
            logger.warning(f"SpeakingEvaluation validation failed for user {user_id}: {message}")
            return {"error": message, "code": "INVALID_INPUT"}, 400

        # 3. ASR Transcription
        asr_result = self.speaking_evaluator.transcribe_audio(audio_file, timeout=30)
        if not asr_result:
            logger.error(f"ASR failed for user {user_id}: No speech detected or transcription error")
            return {
                "error": "NO_SPEECH_DETECTED",
                "message": "No speech detected in the audio file. Please ensure your microphone is working."
            }, 400

        transcript_text = asr_result['transcript']
        logger.info(f"ASR Success for user {user_id}. Transcript length: {len(transcript_text)}")

        # 4. LLM Analysis (Speaking Scoring)
        result = self.speaking_evaluator.analyze_speaking(
            transcript_text, question, mode=question.mode
        )
        if not result:
            logger.error(f"SpeakingEvaluator.analyze returned None for user {user_id}")
            return {
                "error": "SERVICE_UNAVAILABLE",
                "message": "AI service temporarily unavailable. Try again later."
            }, 503

        # 5. Save Audio File to Storage (File System for now, can be S3 later)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        # Reset file pointer to beginning
        audio_file.seek(0)
        
        # Generate unique filename
        file_extension = os.path.splitext(audio_file.name)[1]
        unique_filename = f"speaking/{user_id}/{uuid.uuid4()}{file_extension}"
        
        try:
            audio_path = default_storage.save(unique_filename, ContentFile(audio_file.read()))
            logger.info(f"Audio file saved to: {audio_path}")
        except Exception as e:
            logger.error(f"Failed to save audio file: {str(e)}")
            audio_path = f"uploads/{unique_filename}"  # Fallback path

        # 6. Data Persistence (Layer 3)
        try:
            # Use explicit 'team7' database to ensure data is saved to team's database
            eval_obj = Evaluation.objects.using('team7').create(
                user_id=user_id,
                question=question,
                exam=question.exam,  # Save exam reference for history tracking
                task_type="speaking",
                audio_path=audio_path,
                transcript_text=transcript_text,
                overall_score=result.get('overall_score'),
                ai_feedback=result.get('feedback'),
                rubric_version_id=SpeakingEvaluator.RUBRIC_VERSION
            )

            # Save detailed criterion scores
            for crit in result.get('criteria', []):
                DetailedScore.objects.using('team7').create(
                    evaluation=eval_obj,
                    criterion=crit.get('name'),
                    score_value=crit.get('score'),
                    comment=crit.get('comment')
                )

            logger.info(f"Speaking evaluation created: {eval_obj.evaluation_id} for user {user_id}")

            # 7. Response (FR-API-02)
            return {
                "status": "success",
                "evaluation_id": str(eval_obj.evaluation_id),
                "overall_score": float(eval_obj.overall_score) if eval_obj.overall_score else None,
                "feedback": eval_obj.ai_feedback,
                "transcript": transcript_text,
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
            logger.exception(f"Error saving speaking evaluation for user {user_id}: {str(e)}")
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
            evaluations = Evaluation.objects.using('team7').filter(
                user_id=user_id
            ).select_related('question', 'exam').prefetch_related('detailed_scores').order_by('-created_at')[:limit]

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
                    "exam_id": str(eval_obj.exam.exam_id) if eval_obj.exam else None,
                    "exam_name": eval_obj.exam.title if eval_obj.exam else "Unknown Exam",
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


class AnalyticsService:
    """Analytics and trend calculation service (UC-03, FR-MON-02).
    
    Provides statistical analysis of user performance over time.
    Calculates trends, averages, and improvement metrics.
    """

    @staticmethod
    def calculate_moving_average(scores, window_size=3):
        """Calculate moving average for trend smoothing.
        
        Args:
            scores: List of numeric scores
            window_size: Number of data points to average (default 3)
            
        Returns:
            list: Moving averages (same length as input, padded with None)
        """
        if not scores or len(scores) < window_size:
            return [None] * len(scores)
        
        moving_avgs = []
        for i in range(len(scores)):
            if i < window_size - 1:
                moving_avgs.append(None)
            else:
                window = scores[i - window_size + 1:i + 1]
                avg = sum(window) / window_size
                moving_avgs.append(round(avg, 2))
        
        return moving_avgs

    @staticmethod
    def calculate_improvement_rate(scores):
        """Calculate overall improvement rate (first to last score).
        
        Args:
            scores: List of numeric scores (chronological order)
            
        Returns:
            dict: {
                'improvement': float (percentage change),
                'trend': str ('improving', 'declining', 'stable')
            }
        """
        if not scores or len(scores) < 2:
            return {'improvement': 0.0, 'trend': 'insufficient_data'}
        
        first_score = scores[0]
        last_score = scores[-1]
        
        if first_score == 0:
            return {'improvement': 0.0, 'trend': 'stable'}
        
        improvement = ((last_score - first_score) / first_score) * 100
        
        if improvement > 5:
            trend = 'improving'
        elif improvement < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'improvement': round(improvement, 2),
            'trend': trend
        }

    @staticmethod
    def calculate_statistics(scores):
        """Calculate basic statistics for a score set.
        
        Args:
            scores: List of numeric scores
            
        Returns:
            dict: Statistics including mean, min, max, median
        """
        if not scores:
            return {
                'mean': None,
                'min': None,
                'max': None,
                'median': None,
                'count': 0
            }
        
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        
        return {
            'mean': round(sum(scores) / n, 2),
            'min': min(scores),
            'max': max(scores),
            'median': sorted_scores[n // 2] if n % 2 == 1 else round((sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2, 2),
            'count': n
        }

    def get_user_analytics(self, user_id, limit=50):
        """Enhanced analytics with trends and statistics (UC-03).
        
        Args:
            user_id: UUID of student
            limit: Max records to analyze
            
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
                    "attempts": [],
                    "analytics": None
                }, 200

            # Reverse to get chronological order for trend calculation
            evaluations_list = list(evaluations)
            evaluations_list.reverse()

            # Extract scores by task type
            writing_scores = []
            speaking_scores = []
            all_scores = []
            attempts = []

            for eval_obj in evaluations_list:
                score = float(eval_obj.overall_score) if eval_obj.overall_score else None
                
                if score is not None:
                    all_scores.append(score)
                    if eval_obj.task_type == 'writing':
                        writing_scores.append(score)
                    elif eval_obj.task_type == 'speaking':
                        speaking_scores.append(score)
                
                attempts.append({
                    "evaluation_id": str(eval_obj.evaluation_id),
                    "task_type": eval_obj.task_type,
                    "question_id": str(eval_obj.question.question_id),
                    "overall_score": score,
                    "created_at": eval_obj.created_at.isoformat(),
                    "criteria": [
                        {
                            "name": ds.criterion,
                            "score": float(ds.score_value)
                        }
                        for ds in eval_obj.detailed_scores.all()
                    ]
                })

            # Reverse attempts back to descending order for display
            attempts.reverse()

            # Calculate analytics
            analytics = {
                'overall': {
                    'statistics': self.calculate_statistics(all_scores),
                    'improvement': self.calculate_improvement_rate(all_scores),
                    'moving_average': self.calculate_moving_average(all_scores, window_size=3)
                },
                'writing': {
                    'statistics': self.calculate_statistics(writing_scores),
                    'improvement': self.calculate_improvement_rate(writing_scores),
                } if writing_scores else None,
                'speaking': {
                    'statistics': self.calculate_statistics(speaking_scores),
                    'improvement': self.calculate_improvement_rate(speaking_scores),
                } if speaking_scores else None
            }

            logger.info(f"Analytics calculated for user {user_id}: {analytics['overall']['statistics']['count']} evaluations")

            return {
                "status": "success",
                "total_attempts": len(attempts),
                "attempts": attempts,
                "analytics": analytics
            }, 200

        except Exception as e:
            logger.exception(f"Error fetching analytics for user {user_id}: {str(e)}")
            return {
                "error": "INTERNAL_ERROR",
                "message": "Failed to retrieve analytics."
            }, 500