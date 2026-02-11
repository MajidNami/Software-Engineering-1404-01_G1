import json
import os
import logging
import random
import threading
from django.db import close_old_connections
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from core.auth import api_login_required
from .models import (
    Submission, WritingSubmission, ListeningSubmission, 
    AssessmentResult, SubmissionType, AnalysisStatus,
    QuestionCategory, Question
)
from .services import assess_writing, assess_speaking

logger = logging.getLogger(__name__)

TEAM_NAME = "team11"


def _process_writing_assessment(submission_id, topic, text_body, word_count):
    try:
        close_old_connections()
        logger.info(f"Writing background task started: {submission_id}")
        assessment_result = assess_writing(topic, text_body, word_count)
        submission = Submission.objects.using('team11').get(submission_id=submission_id)

        if assessment_result.get('success'):
            submission.overall_score = assessment_result['overall_score']
            submission.status = AnalysisStatus.COMPLETED
            submission.save()

            AssessmentResult.objects.using('team11').update_or_create(
                submission=submission,
                defaults={
                    'grammar_score': assessment_result['grammar_score'],
                    'vocabulary_score': assessment_result['vocabulary_score'],
                    'coherence_score': assessment_result['coherence_score'],
                    'fluency_score': assessment_result['fluency_score'],
                    'feedback_summary': assessment_result['feedback_summary'],
                    'suggestions': assessment_result['suggestions'],
                }
            )
            logger.info(f"Writing assessment completed: {submission.submission_id}, score: {submission.overall_score}")
            return

        error_msg = 'ارزیابی ناموفق بود. لطفاً دوباره تلاش کنید.'
        submission.status = AnalysisStatus.FAILED
        submission.save()
        AssessmentResult.objects.using('team11').update_or_create(
            submission=submission,
            defaults={
                'feedback_summary': error_msg,
                'suggestions': [],
            }
        )
        logger.error(f"Writing assessment failed: {submission.submission_id}, error: {assessment_result.get('error')}")
    except Exception as e:
        logger.error(f"Background writing assessment error: {e}", exc_info=True)
        try:
            close_old_connections()
            submission = Submission.objects.using('team11').get(submission_id=submission_id)
            submission.status = AnalysisStatus.FAILED
            submission.save()
        except Exception:
            pass


def _process_listening_assessment(submission_id, listening_detail_pk, audio_file_path, topic, duration, temp_file_path=None):
    try:
        close_old_connections()
        logger.info(f"Speaking background task started: {submission_id}")
        assessment_result = assess_speaking(topic, audio_file_path, duration)
        submission = Submission.objects.using('team11').get(submission_id=submission_id)
        listening_detail = ListeningSubmission.objects.using('team11').get(pk=listening_detail_pk)

        if assessment_result.get('success'):
            listening_detail.transcription = assessment_result.get('transcription', '')
            listening_detail.save()

            submission.overall_score = assessment_result['overall_score']
            submission.status = AnalysisStatus.COMPLETED
            submission.save()

            AssessmentResult.objects.using('team11').update_or_create(
                submission=submission,
                defaults={
                    'pronunciation_score': assessment_result['pronunciation_score'],
                    'fluency_score': assessment_result['fluency_score'],
                    'vocabulary_score': assessment_result['vocabulary_score'],
                    'grammar_score': assessment_result['grammar_score'],
                    'coherence_score': assessment_result['coherence_score'],
                    'feedback_summary': assessment_result['feedback_summary'],
                    'suggestions': assessment_result['suggestions'],
                }
            )
            logger.info(f"Speaking assessment completed: {submission.submission_id}, score: {submission.overall_score}")
            return

        raw_error = assessment_result.get('error', '')
        error_msg = 'ارزیابی ناموفق بود. لطفاً دوباره تلاش کنید.'
        if 'no speech' in str(raw_error).lower():
            error_msg = 'صدایی تشخیص داده نشد. لطفاً واضح‌تر صحبت کنید.'

        submission.status = AnalysisStatus.FAILED
        submission.save()
        AssessmentResult.objects.using('team11').update_or_create(
            submission=submission,
            defaults={
                'feedback_summary': error_msg,
                'suggestions': [],
            }
        )
        logger.error(f"Speaking assessment failed: {submission.submission_id}, error: {raw_error}")
    except Exception as e:
        logger.error(f"Background listening assessment error: {e}", exc_info=True)
        try:
            close_old_connections()
            submission = Submission.objects.using('team11').get(submission_id=submission_id)
            submission.status = AnalysisStatus.FAILED
            submission.save()
        except Exception:
            pass
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temp file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    """Landing page for Team 11 microservice"""
    return render(request, f"{TEAM_NAME}/index.html")


@api_login_required
def dashboard(request):
    """Dashboard showing user's submission history"""
    user_id = request.user.id
    
    # Get all submissions for the user with related data
    submissions = Submission.objects.using('team11').filter(user_id=user_id).select_related(
        'assessment_result',
        'writing_details',
        'listening_details'
    ).order_by('-created_at')
    
    completed_submissions = submissions.filter(status=AnalysisStatus.COMPLETED, overall_score__isnull=False)
    completed_count = completed_submissions.count()

    writing_completed = completed_submissions.filter(submission_type=SubmissionType.WRITING).order_by('created_at')
    speaking_completed = completed_submissions.filter(submission_type=SubmissionType.LISTENING).order_by('created_at')

    writing_avg = writing_completed.aggregate(avg=Avg('overall_score'))['avg']
    speaking_avg = speaking_completed.aggregate(avg=Avg('overall_score'))['avg']

    writing_series = [
        {
            'date': s.created_at.strftime('%Y/%m/%d'),
            'score': s.overall_score,
        }
        for s in writing_completed
    ]
    speaking_series = [
        {
            'date': s.created_at.strftime('%Y/%m/%d'),
            'score': s.overall_score,
        }
        for s in speaking_completed
    ]

    context = {
        'submissions': submissions,
        'completed_count': completed_count,
        'writing_avg': round(writing_avg, 2) if writing_avg is not None else 0,
        'speaking_avg': round(speaking_avg, 2) if speaking_avg is not None else 0,
        'writing_series': writing_series,
        'speaking_series': speaking_series,
    }
    return render(request, f"{TEAM_NAME}/dashboard.html", context)


@api_login_required
def start_exam(request):
    """Page to select exam type and category"""
    writing_categories = QuestionCategory.objects.using('team11').filter(
        question_type=SubmissionType.WRITING,
        is_active=True
    ).prefetch_related('questions')
    
    listening_categories = QuestionCategory.objects.using('team11').filter(
        question_type=SubmissionType.LISTENING,
        is_active=True
    ).prefetch_related('questions')
    
    context = {
        'writing_categories': writing_categories,
        'listening_categories': listening_categories,
    }
    return render(request, f"{TEAM_NAME}/start_exam.html", context)


@api_login_required
def writing_exam(request):
    """Page for writing exam - random question from selected category"""
    category_id = request.GET.get('category')
    
    if category_id:
        questions = Question.objects.using('team11').filter(
            category_id=category_id,
            category__question_type=SubmissionType.WRITING,
            is_active=True
        )
    else:
        questions = Question.objects.using('team11').filter(
            category__question_type=SubmissionType.WRITING,
            is_active=True
        )
    
    question = random.choice(list(questions)) if questions.exists() else None
    
    context = {
        'question': question,
        'has_question': question is not None,
    }
    return render(request, f"{TEAM_NAME}/writing_exam.html", context)


@api_login_required
def listening_exam(request):
    """Page for listening exam - random question from selected category"""
    category_id = request.GET.get('category')
    
    if category_id:
        questions = Question.objects.using('team11').filter(
            category_id=category_id,
            category__question_type=SubmissionType.LISTENING,
            is_active=True
        )
    else:
        questions = Question.objects.using('team11').filter(
            category__question_type=SubmissionType.LISTENING,
            is_active=True
        )
    
    question = random.choice(list(questions)) if questions.exists() else None
    
    context = {
        'question': question,
        'has_question': question is not None,
    }
    return render(request, f"{TEAM_NAME}/listening_exam.html", context)


@csrf_exempt
@require_POST
@api_login_required
def submit_writing(request):
    """API endpoint to submit writing task"""
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id', '')
        topic = data.get('topic', '')
        text_body = data.get('text_body', '')
        
        if not text_body:
            return JsonResponse({'error': 'متن ارسالی نمی‌تواند خالی باشد.'}, status=400)
        
        word_count = len(text_body.split())
        
        # Get question object if provided
        question = None
        if question_id:
            try:
                question = Question.objects.using('team11').get(question_id=question_id)
            except Question.DoesNotExist:
                pass
        
        # Create submission with pending status
        submission = Submission.objects.using('team11').create(
            user_id=request.user.id,
            submission_type=SubmissionType.WRITING,
            status=AnalysisStatus.IN_PROGRESS
        )
        
        # Create writing details
        WritingSubmission.objects.using('team11').create(
            submission=submission,
            question=question,
            topic=topic,
            text_body=text_body,
            word_count=word_count
        )
        
        logger.info(f"Queueing writing submission {submission.submission_id} for user {request.user.id}")

        thread = threading.Thread(
            target=_process_writing_assessment,
            args=(submission.submission_id, topic, text_body, word_count),
            daemon=True
        )
        thread.start()

        return JsonResponse({
            'success': True,
            'submission_id': str(submission.submission_id),
            'status': 'processing',
            'message': 'در حال پردازش... لطفاً صبر کنید.'
        }, status=202)
        
    except Exception as e:
        logger.error(f"Error in submit_writing: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
@api_login_required
def submit_listening(request):
    """API endpoint to submit listening (audio) task"""
    logger.info("=" * 80)
    logger.info("SUBMIT LISTENING ENDPOINT HIT!")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Content-Length: {request.META.get('CONTENT_LENGTH', 'unknown')}")
    logger.info(f"User authenticated: {request.user.is_authenticated if hasattr(request, 'user') else 'No user'}")
    logger.info("=" * 80)
    
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id', '')
        topic = data.get('topic', '')
        audio_data = data.get('audio_data', '')
        audio_url = data.get('audio_url', audio_data)  # Support both old and new format
        duration = data.get('duration_seconds', 0)
        
        if not audio_url and not audio_data:
            return JsonResponse({'error': 'فایل صوتی ارسال نشده است.'}, status=400)
        
        user_id = request.user.id
        
        # Get question object if provided
        question = None
        if question_id:
            try:
                question = Question.objects.using('team11').get(question_id=question_id)
            except Question.DoesNotExist:
                pass
        
        # Create submission with pending status
        submission = Submission.objects.using('team11').create(
            user_id=user_id,
            submission_type=SubmissionType.LISTENING,
            status=AnalysisStatus.IN_PROGRESS
        )
        
        # Create listening details (without transcription initially)
        listening_detail = ListeningSubmission.objects.using('team11').create(
            submission=submission,
            question=question,
            topic=topic,
            audio_file_url=audio_url,
            duration_seconds=duration
        )
        
        logger.info(f"Processing listening submission {submission.submission_id} for user {request.user.id}")
        
        # Handle base64 audio data
        audio_file_path = None
        temp_file = None
        
        try:
            if audio_url.startswith('data:audio'):
                # It's a base64 data URL - decode and save to temp file
                import base64
                import tempfile
                
                logger.info(f"Processing base64 audio data, length: {len(audio_url)}")
                
                # Extract the base64 data (remove the data URL prefix)
                try:
                    header, encoded = audio_url.split(',', 1)
                    audio_bytes = base64.b64decode(encoded)
                    logger.info(f"Decoded audio bytes: {len(audio_bytes)} bytes")
                except Exception as decode_error:
                    raise ValueError(f"Failed to decode base64 audio: {decode_error}")
                
                # Create temp file with appropriate extension
                suffix = '.webm' if 'webm' in header else '.wav'
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp_file.write(audio_bytes)
                temp_file.close()
                audio_file_path = temp_file.name
                
                logger.info(f"Saved base64 audio to temp file: {audio_file_path} (size: {len(audio_bytes)} bytes)")
                
                # Verify file exists
                if not os.path.exists(audio_file_path):
                    raise ValueError(f"Temp file was not created: {audio_file_path}")
                
            elif audio_url.startswith('http://') or audio_url.startswith('https://'):
                # For remote URLs, you would need to download the file first
                logger.warning(f"Remote audio URL provided: {audio_url}. Download logic needed.")
                audio_file_path = audio_url  # Placeholder - needs implementation
            else:
                # Local file path (relative to MEDIA_ROOT or absolute)
                if not audio_url.startswith('/') and not audio_url[1:3] == ':\\':
                    # Relative path - join with MEDIA_ROOT
                    audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_url)
                else:
                    audio_file_path = audio_url
            
            if not audio_file_path or not os.path.exists(audio_file_path):
                raise ValueError(f"Audio file not found or could not be created: {audio_file_path}")

            logger.info(f"Queueing AI assessment for audio file: {audio_file_path}")
            thread = threading.Thread(
                target=_process_listening_assessment,
                args=(submission.submission_id, listening_detail.pk, audio_file_path, topic, duration, temp_file.name if temp_file else None),
                daemon=True
            )
            thread.start()

            return JsonResponse({
                'success': True,
                'submission_id': str(submission.submission_id),
                'status': 'processing',
                'message': 'در حال پردازش... لطفاً صبر کنید.'
            }, status=202)
            
        except Exception as audio_error:
            logger.error(f"Error processing audio file: {audio_error}", exc_info=True)
            # Mark as failed
            submission.status = AnalysisStatus.FAILED
            submission.save()
            
            return JsonResponse({
                'success': False,
                'submission_id': str(submission.submission_id),
                'error': f'پردازش صوت با خطا مواجه شد: {str(audio_error)}',
                'message': 'ارسال ذخیره شد اما پردازش صوت ناموفق بود. لطفاً دوباره تلاش کنید.'
            }, status=500)
        
    except Exception as e:
        logger.error(f"Error in submit_listening: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@api_login_required
def submission_detail(request, submission_id):
    """View detailed results for a specific submission"""
    submission = get_object_or_404(
        Submission.objects.using('team11').select_related('assessment_result'),
        submission_id=submission_id,
        user_id=request.user.id
    )

    if submission.status in [AnalysisStatus.IN_PROGRESS, AnalysisStatus.PENDING]:
        return render(request, f"{TEAM_NAME}/submission_detail.html", {
            'submission': submission,
            'details': None,
            'result': None,
            'processing': True,
        })
    
    # Get type-specific details using select_related (OneToOne relationship)
    details = None
    if submission.submission_type == SubmissionType.WRITING:
        try:
            details = submission.writing_details
        except WritingSubmission.DoesNotExist:
            details = None
    else:
        try:
            details = submission.listening_details
        except ListeningSubmission.DoesNotExist:
            details = None
    
    context = {
        'submission': submission,
        'details': details,
        'result': submission.assessment_result if hasattr(submission, 'assessment_result') else None,
        'processing': False,
    }
    return render(request, f"{TEAM_NAME}/submission_detail.html", context)


@api_login_required
@require_http_methods(["GET"])
def submission_status(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.using('team11').select_related('assessment_result'),
        submission_id=submission_id,
        user_id=request.user.id
    )

    if submission.status == AnalysisStatus.IN_PROGRESS:
        return JsonResponse({'status': 'in_progress'})

    if submission.status == AnalysisStatus.COMPLETED:
        return JsonResponse({
            'status': 'completed',
            'score': submission.overall_score,
            'message': 'ارزیابی با موفقیت انجام شد.'
        })

    error_message = None
    if hasattr(submission, 'assessment_result') and submission.assessment_result:
        error_message = submission.assessment_result.feedback_summary

    return JsonResponse({
        'status': 'failed',
        'message': error_message or 'ارزیابی ناموفق بود. لطفاً دوباره تلاش کنید.'
    })