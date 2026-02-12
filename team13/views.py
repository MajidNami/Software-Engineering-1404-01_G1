import json

from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.db import models
from rest_framework.response import Response
from rest_framework import status

from core.auth import api_login_required
from team13.models.question import Question
from team13.models.prompt import Prompt
from team13.models.report import ViewedQuestion, WritingGradeResult, SpeakingGradeResult
from team13.services import ollama_service, whisper_service

TEAM_NAME = "team13"


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


@require_GET
@api_login_required
def get_question(request):
    """Get a random question for the user to answer"""
    question_type = request.query_params.get('type', None)
    if question_type not in Question.QUESTION_TYPES:
        return Response({'error': 'Invalid question type'}, status=status.HTTP_404_NOT_FOUND)
    question = Question.objects.filter(question_type=question_type).order_by('?').first() # Get a random question
    if not question:
        return Response({'error': 'No questions available'}, status=status.HTTP_404_NOT_FOUND)

    # Track that user viewed this question
    ViewedQuestion.objects.create(user=request.user, question=question)

    return Response({
        'id': question.id,
        'title': question.title,
        'text': question.text,
        'type': question.question_type,
    }, status=status.HTTP_200_OK)


@require_POST
@api_login_required
def submit_response(request):
    # Extract question object.
    question_id = request.data.get('question_id')
    if not question_id:
        return Response({'error': 'question_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    question = get_object_or_404(Question, id=question_id)

    # Extract student response.
    if question.question_type == Question.WRITING_QUESTION_TYPE:
        student_response = request.data.get('response')
    else:
        audio_file = request.FILES.get('audio_file')
        if not audio_file:
            return Response({'error': 'audio_file is required for speaking questions'},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            student_response = whisper_service.transcribe(audio_file)
        except Exception as e:
            return Response({'error': f'Transcription failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not student_response:
        return Response({'error': 'student response is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Get an active prompt, we assume that there is no difference to use which active prompt.
    prompt = Prompt.objects.filter(is_active=True).first()
    if not prompt:
        return Response({'error': 'No active prompt was found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    full_prompt = prompt.get_prompt(question, student_response) # Build prompt and get evaluation
    try:
        result_text = ollama_service.grade(full_prompt)
        result_json = json.loads(result_text)
    except Exception as e:
        return Response({'error': f'Grading failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Save to appropriate grade model
    if question.question_type == Question.WRITING_QUESTION_TYPE:
        category_scores = result_json.get('category_scores', {})
        grade_result = WritingGradeResult.objects.create(
            user=request.user,
            question=question,
            score=result_json.get('score', 0),
            task_achievement=category_scores.get('task_achievement', 0),
            coherence=category_scores.get('coherence', 0),
            vocabulary=category_scores.get('vocabulary', 0),
            grammar=category_scores.get('grammar', 0),
            mechanics=category_scores.get('mechanics', 0),
        )
    else:
        category_scores = result_json.get('category_scores', {})
        grade_result = SpeakingGradeResult.objects.create(
            user=request.user,
            question=question,
            score=result_json.get('score', 0),
            delivery=category_scores.get('delivery', 0),
            language_use=category_scores.get('language_use', 0),
            topic_development=category_scores.get('topic_development', 0),
        )

    return Response({
        'grade_id': grade_result.id,
        'score': result_json.get('score'),
        'category_scores': result_json.get('category_scores'),
        'feedback': result_json.get('feedback'),
    }, status=status.HTTP_201_CREATED)


@require_GET
@api_login_required
def get_user_report(request):
    """Get user performance reports and history"""
    user = request.user
    writing_grades = WritingGradeResult.objects.filter(user=user).select_related('question')
    speaking_grades = SpeakingGradeResult.objects.filter(user=user).select_related('question')
    viewed_counts = ViewedQuestion.objects.filter(user=user).aggregate(
        total_writing=models.Count('id', filter=models.Q(question__question_type=Question.WRITING_QUESTION_TYPE)),
        total_speaking=models.Count('id', filter=models.Q(question__question_type=Question.SPEAKING_QUESTION_TYPE))
    )
    total_writing = viewed_counts['total_writing']
    total_speaking = viewed_counts['total_speaking']

    writing_agg = writing_grades.aggregate(
        total_score=models.Sum('score'),
        avg_grammar=models.Avg('grammar'),
        avg_vocabulary=models.Avg('vocabulary'),
        avg_coherence=models.Avg('coherence'),
        scores_list=models.JSONArrayAgg('score', ordering='created'),
        dates_list=models.JSONArrayAgg('created', ordering='created')
    )

    speaking_agg = speaking_grades.aggregate(
        total_score=models.Sum('score'),
        avg_delivery=models.Avg('delivery'),
        avg_language_use=models.Avg('language_use'),
        scores_list=models.JSONArrayAgg('score', ordering='created'),
        dates_list=models.JSONArrayAgg('created', ordering='created')
    )

    avg_writing_score = (writing_agg['total_score'] or 0) / total_writing if total_writing > 0 else None
    avg_speaking_score = (speaking_agg['total_score'] or 0) / total_speaking if total_speaking > 0 else None

    last_writing = writing_grades.order_by('-created')[:10]
    last_speaking = speaking_grades.order_by('-created')[:10]

    last_ten_submissions = []
    for grade in last_writing:
        last_ten_submissions.append({
            'id': grade.id,
            'type': 'writing',
            'question_title': grade.question.title,
            'score': grade.score,
            'category_scores': {
                'task_achievement': grade.task_achievement,
                'coherence': grade.coherence,
                'vocabulary': grade.vocabulary,
                'grammar': grade.grammar,
                'mechanics': grade.mechanics,
            },
            'date': grade.created,
        })
    for grade in last_speaking:
        last_ten_submissions.append({
            'id': grade.id,
            'type': 'speaking',
            'question_title': grade.question.title,
            'score': grade.score,
            'category_scores': {
                'delivery': grade.delivery,
                'language_use': grade.language_use,
                'topic_development': grade.topic_development,
            },
            'date': grade.created,
        })
    last_ten_submissions.sort(key=lambda x: x['date'], reverse=True)
    last_ten_submissions = last_ten_submissions[:10]

    weak_areas = []
    if writing_grades.exists():
        if writing_agg['avg_grammar'] is not None:
            weak_areas.append({'area': 'Grammar', 'avg_score': writing_agg['avg_grammar']})
        if writing_agg['avg_vocabulary'] is not None:
            weak_areas.append({'area': 'Vocabulary', 'avg_score': writing_agg['avg_vocabulary']})
        if writing_agg['avg_coherence'] is not None:
            weak_areas.append({'area': 'Coherence', 'avg_score': writing_agg['avg_coherence']})

    if speaking_grades.exists():
        if speaking_agg['avg_delivery'] is not None:
            weak_areas.append({'area': 'Pronunciation', 'avg_score': speaking_agg['avg_delivery']})
        if speaking_agg['avg_language_use'] is not None:
            weak_areas.append({'area': 'Grammar', 'avg_score': speaking_agg['avg_language_use']})

    weak_areas.sort(key=lambda x: x['avg_score'])
    weak_areas = weak_areas[:3]

    return Response({
        'summary': {
            'total_attempts': total_writing + total_speaking,
            'writing_attempts': total_writing,
            'speaking_attempts': total_speaking,
            'average_writing_score': round(avg_writing_score, 2),
            'average_speaking_score': round(avg_speaking_score, 2),
        },
        'weakest_areas': weak_areas,
        'recent_submissions': last_ten_submissions,
        'progress': {
            'writing_scores': writing_agg['scores_list'] or [],
            'writing_dates': writing_agg['dates_list'] or [],
            'speaking_scores': speaking_agg['scores_list'] or [],
            'speaking_dates': speaking_agg['dates_list'] or [],
        }
    })
