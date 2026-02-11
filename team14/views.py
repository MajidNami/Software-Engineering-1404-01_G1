from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from core.auth import api_login_required
from django.contrib.auth.decorators import login_required
from .models import UserSession, Passage, Question, Option
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Passage, Question, UserSession, UserAnswer, AntiCheatLog
import json


TEAM_NAME = "team14"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

def training_levels(request):
    return render(request, 'team14/training_levels.html')


def index(request):

    last_session = UserSession.objects.filter(
        user=request.user,
        mode='exam',
        end_time__isnull=False,
        scaled_score__isnull=False
    ).order_by('-end_time').first()


    context = {
        'last_score': last_session.scaled_score if last_session else None,
        'has_taken_exam': last_session is not None
    }

    return render(request, 'team14/index.html', context)


login_required(login_url='auth')


def easy_level(request):
    # گرفتن تمام passage های سطح آسان
    passages = Passage.objects.filter(
        difficulty_level='easy'
    ).prefetch_related('questions__options').order_by('-created_at')

    # آماده کردن داده‌ها برای ارسال به template
    passages_data = []
    for passage in passages:
        # شمارش تعداد سوالات
        question_count = passage.questions.count()

        # محاسبه زمان تخمینی (حدود 1 دقیقه برای هر 75 کلمه + 1 دقیقه برای هر سوال)
        estimated_time = (passage.text_length // 75) + question_count

        passages_data.append({
            'id': passage.id,
            'title': passage.title,
            'topic': passage.get_topic_display(),  # نمایش نام فارسی topic
            'text_length': passage.text_length,
            'question_count': question_count,
            'estimated_time': estimated_time,
            'icon': get_topic_icon(passage.topic),  # تابع کمکی برای آیکون
        })

    context = {
        'passages': passages_data,
        'difficulty': 'آسان',
        'total_passages': len(passages_data),
    }

    return render(request, 'team14/practice_passages.html', context)



def mid_level(request):
    # گرفتن تمام passage های سطح متوسط
    passages = Passage.objects.filter(
        difficulty_level='medium'
    ).prefetch_related('questions__options').order_by('-created_at')

    passages_data = []
    for passage in passages:
        question_count = passage.questions.count()
        estimated_time = (passage.text_length // 75) + question_count

        passages_data.append({
            'id': passage.id,
            'title': passage.title,
            'topic': passage.get_topic_display(),
            'text_length': passage.text_length,
            'question_count': question_count,
            'estimated_time': estimated_time,
            'icon': get_topic_icon(passage.topic),
        })

    context = {
        'passages': passages_data,
        'difficulty': 'متوسط',
        'total_passages': len(passages_data),
    }

    return render(request, 'team14/practice_passages.html', context)



def hard_level(request):
    # گرفتن تمام passage های سطح سخت
    passages = Passage.objects.filter(
        difficulty_level='hard'
    ).prefetch_related('questions__options').order_by('-created_at')

    passages_data = []
    for passage in passages:
        question_count = passage.questions.count()
        estimated_time = (passage.text_length // 75) + question_count

        passages_data.append({
            'id': passage.id,
            'title': passage.title,
            'topic': passage.get_topic_display(),
            'text_length': passage.text_length,
            'question_count': question_count,
            'estimated_time': estimated_time,
            'icon': get_topic_icon(passage.topic),
        })

    context = {
        'passages': passages_data,
        'difficulty': 'سخت',
        'total_passages': len(passages_data),
    }

    return render(request, 'team14/practice_passages.html', context)


def get_topic_icon(topic):
        icons = {
            'biology': '🧬',
            'history': '📜',
            'astronomy': '🌌',
            'geology': '🌍',
            'anthropology': '🗿',
        }
        return icons.get(topic, '📚')

def Exam_Page(request):
    return render(request, 'team14/Exam_Page.html')




def practice_page(request, passage_id):
    if not request.user.is_authenticated:
        return redirect('login')

    passage = get_object_or_404(
        Passage.objects.prefetch_related('questions__options'),
        id=passage_id
    )

    questions_qs = passage.questions.all().order_by('id')

    # ✅ JSON برای JS
    questions_data = []
    for q in questions_qs:
        questions_data.append({
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": [
                {"id": opt.id, "text": opt.text}
                for opt in q.options.all()
            ]
        })

    # ✅ استفاده درست از user_id
    session, created = UserSession.objects.get_or_create(
        user_id=request.user.id,
        passage=passage,
        mode='practice',
        defaults={'start_time': timezone.now()}
    )

    user_answers = {
        ans.question_id: ans.selected_option_id
        for ans in UserAnswer.objects.filter(session=session)
    }

    elapsed = (timezone.now() - session.start_time).seconds
    time_left = max(0, 18 * 60 - elapsed)

    context = {
        'passage': passage,
        'questions': json.dumps(questions_data),
        'total_questions': questions_qs.count(),
        'session': session,
        'user_answers': json.dumps(user_answers),
        'time_left': time_left,
    }

    return render(request, 'team14/Practice_Page.html', context)


@csrf_exempt
def submit_answer(request):
    if request.method != 'POST' or not request.user.is_authenticated:
        return JsonResponse({'success': False}, status=403)

    try:
        data = json.loads(request.body)

        session = get_object_or_404(
            UserSession,
            id=data['session_id'],
            user_id=request.user.id   # ✅ خیلی مهم
        )

        question = get_object_or_404(
            Question,
            id=data['question_id'],
            passage=session.passage
        )

        answer, created = UserAnswer.objects.get_or_create(
            user_id=request.user.id,
            session=session,
            question=question,
            defaults={'selected_option_id': data['option_id']}
        )

        if not created and answer.selected_option_id != data['option_id']:
            answer.selected_option_id = data['option_id']
            answer.changed_count += 1
            answer.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



def finish_practice(request, session_id):
    session = get_object_or_404(
        UserSession,
        id=session_id,
        user_id=request.user.id
    )

    answers = UserAnswer.objects.filter(session=session)
    correct_count = sum(
        1 for a in answers
        if a.selected_option and a.selected_option.is_correct
    )

    total_questions = session.passage.questions.count()

    if total_questions > 0:
        session.total_score = (correct_count / total_questions) * 100
        session.end_time = timezone.now()
        session.save()

    return redirect('team14:practice_result', session_id=session.id)



