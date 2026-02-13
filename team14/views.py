from django.views.decorators.csrf import csrf_exempt
import random
from core.auth import api_login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Passage
import json
from .models import UserSession, Question, UserAnswer
from django.db.models import Q, Count

TEAM_NAME = "team14"

PRACTICE_TIME_MINUTES = 30


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


def training_levels(request):
    return render(request, 'team14/training_levels.html')


def index(request):
    last_session = UserSession.objects.filter(
        user=request.user,  # فرض شده request.user یک User مدل معتبر است.
        mode='exam',
        end_time__isnull=False
    ).order_by('-end_time').first()

    context = {
        'last_score': last_session.total_score if last_session else None,
        'has_taken_exam': last_session is not None
    }

    return render(request, 'team14/index.html', context)


def get_filtered_passages(difficulty_level, topic=None, text_length=None, search=None):
    """
    تابع کمکی برای فیلتر کردن passage ها
    """
    queryset = Passage.objects.filter(
        difficulty_level=difficulty_level
    ).prefetch_related('questions__options').annotate(
        question_count=Count('questions')
    )

    # فیلتر موضوع
    if topic and topic != 'all':
        queryset = queryset.filter(topic=topic)

    # فیلتر طول متن
    if text_length == 'short':
        queryset = queryset.filter(text_length__lt=500)
    elif text_length == 'medium':
        queryset = queryset.filter(text_length__gte=500, text_length__lte=700)
    elif text_length == 'long':
        queryset = queryset.filter(text_length__gt=700)

    # جستجو در عنوان
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(text__icontains=search)
        )

    return queryset.order_by('-created_at')


def prepare_passages_data(passages):
    """
    آماده‌سازی داده‌های passage برای template
    """
    passages_data = []
    for passage in passages:
        question_count = passage.question_count if hasattr(passage, 'question_count') else passage.questions.count()
        estimated_time = (passage.text_length // 75) + question_count

        passages_data.append({
            'id': passage.id,
            'title': passage.title,
            'topic': passage.get_topic_display(),
            'topic_en': passage.topic,  # برای فیلتر
            'text_length': passage.text_length,
            'question_count': question_count,
            'estimated_time': estimated_time,
            'icon': get_topic_icon(passage.topic),
            'difficulty_level': passage.difficulty_level,
        })

    return passages_data


@login_required(login_url='/auth/')
def easy_level(request):
    # دریافت پارامترهای فیلتر از URL
    topic = request.GET.get('topic', 'all')
    text_length = request.GET.get('text_length', 'all')
    search = request.GET.get('search', '')

    # فیلتر کردن passages
    passages = get_filtered_passages(
        difficulty_level='easy',
        topic=topic if topic != 'all' else None,
        text_length=text_length if text_length != 'all' else None,
        search=search if search else None
    )

    passages_data = prepare_passages_data(passages)

    # آماده‌سازی لیست موضوعات از مدل
    topic_choices = [{'value': choice[0], 'label': choice[1]} for choice in Passage.TOPIC_CHOICES]

    context = {
        'passages': passages_data,
        'difficulty': 'آسان',
        'difficulty_level': 'easy',
        'difficulty_persian': 'آسان',
        'total_passages': len(passages_data),
        'topic_choices': topic_choices,
        'selected_topic': topic,
        'selected_text_length': text_length,
        'search_query': search,
    }

    return render(request, 'team14/practice_passages.html', context)


@login_required(login_url='/auth/')
def mid_level(request):
    topic = request.GET.get('topic', 'all')
    text_length = request.GET.get('text_length', 'all')
    search = request.GET.get('search', '')

    passages = get_filtered_passages(
        difficulty_level='medium',
        topic=topic if topic != 'all' else None,
        text_length=text_length if text_length != 'all' else None,
        search=search if search else None
    )

    passages_data = prepare_passages_data(passages)
    topic_choices = [{'value': choice[0], 'label': choice[1]} for choice in Passage.TOPIC_CHOICES]

    context = {
        'passages': passages_data,
        'difficulty': 'متوسط',
        'difficulty_level': 'medium',
        'difficulty_persian': 'متوسط',
        'total_passages': len(passages_data),
        'topic_choices': topic_choices,
        'selected_topic': topic,
        'selected_text_length': text_length,
        'search_query': search,
    }

    return render(request, 'team14/practice_passages.html', context)


@login_required(login_url='/auth/')
def hard_level(request):
    topic = request.GET.get('topic', 'all')
    text_length = request.GET.get('text_length', 'all')
    search = request.GET.get('search', '')

    passages = get_filtered_passages(
        difficulty_level='hard',
        topic=topic if topic != 'all' else None,
        text_length=text_length if text_length != 'all' else None,
        search=search if search else None
    )

    passages_data = prepare_passages_data(passages)
    topic_choices = [{'value': choice[0], 'label': choice[1]} for choice in Passage.TOPIC_CHOICES]

    context = {
        'passages': passages_data,
        'difficulty': 'سخت',
        'difficulty_level': 'hard',
        'difficulty_persian': 'سخت',
        'total_passages': len(passages_data),
        'topic_choices': topic_choices,
        'selected_topic': topic,
        'selected_text_length': text_length,
        'search_query': search,
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
    return render(request, 'team14/exam_page.html')


@login_required(login_url='/auth/')
def practice_page(request, passage_id):
    if not request.user.is_authenticated:
        return redirect('login')

    passage = get_object_or_404(
        Passage.objects.prefetch_related('questions__options'),
        id=passage_id
    )

    questions_qs = passage.questions.all().order_by('id')

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

    # ✅ بستن session های تمام نشده قبلی
    UserSession.objects.filter(
        user_id=request.user.id,
        passage=passage,
        mode='practice',
        end_time__isnull=True
    ).update(
        end_time=timezone.now(),
        total_score=0
    )

    # ✅ ساخت session جدید
    session = UserSession.objects.create(
        user_id=request.user.id,
        passage=passage,
        mode='practice',  # ✅ حتماً practice
        start_time=timezone.now()
    )

    user_answers = {
        ans.question_id: ans.selected_option_id
        for ans in UserAnswer.objects.filter(session=session)
    }

    time_left = PRACTICE_TIME_MINUTES * 60

    context = {
        'passage': passage,
        'questions': json.dumps(questions_data),
        'total_questions': questions_qs.count(),
        'session': session,
        'user_answers': json.dumps(user_answers),
        'time_left': time_left,
        'IS_EXAM': False,  # ✅ اضافه شد
    }

    return render(request, 'team14/practice_page.html', context)


@csrf_exempt
def submit_answer(request):
    if request.method != 'POST' or not request.user.is_authenticated:
        return JsonResponse({'success': False}, status=403)

    try:
        data = json.loads(request.body)

        session = get_object_or_404(
            UserSession,
            id=data['session_id'],
            user_id=str(request.user.id)
        )

        # ✅ بررسی زمان
        if session.start_time:
            elapsed = (timezone.now() - session.start_time).total_seconds()
            if elapsed > PRACTICE_TIME_MINUTES * 60:
                return JsonResponse({
                    'success': False,
                    'error': 'زمان تمرین به پایان رسیده است'
                }, status=400)

        question = get_object_or_404(
            Question,
            id=data['question_id'],
            passage=session.passage
        )

        user_answer, created = UserAnswer.objects.get_or_create(
            session=session,
            question=question,
            defaults={
                'selected_option_id': data['option_id'],
                'is_correct': False,  # ✅ مهم
                'response_time': 0  # ✅ مهم
            }
        )

        # اگر قبلاً وجود داشته و جواب عوض شده
        if not created and user_answer.selected_option_id != data['option_id']:
            user_answer.selected_option_id = data['option_id']
            user_answer.changed_count += 1
            user_answer.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def finish_practice(request, session_id):
    session = get_object_or_404(
        UserSession,
        id=session_id,
        user_id=str(request.user.id)  # ✅ باز هم، اطمینان از نوع داده
    )

    answers = UserAnswer.objects.filter(session=session)
    correct_count = 0

    for answer in answers:
        # اگر selected_option null باشد، این شرط اجرا نمی‌شود
        # و is_correct به صورت پیش‌فرض False خواهد ماند یا باید صراحتاً False شود.
        if answer.selected_option and answer.selected_option.is_correct:
            correct_count += 1
            answer.is_correct = True
        else:
            answer.is_correct = False
        answer.save()

    total_questions = session.passage.questions.count()

    # اطمینان از اینکه session.total_score و session.end_time فقط یک بار مقداردهی می‌شوند
    # و اگر قبلاً اتمام یافته، دوباره تغییر نکند، مگر اینکه منطق خاصی برای re-evaluate باشد.
    if session.end_time is None:  # فقط اگر هنوز تمام نشده باشد
        if total_questions > 0:
            session.total_score = (correct_count / total_questions) * 100
        else:
            session.total_score = 0  # اگر سوالی نباشد نمره 0
        session.end_time = timezone.now()
        session.save()

    return redirect('practice_result', session_id=session.id)


def practice_result(request, session_id):
    session = get_object_or_404(
        UserSession,
        id=session_id,
        user_id=str(request.user.id)  # ✅ باز هم، اطمینان از نوع داده (char)
    )

    questions = Question.objects.filter(
        passage=session.passage
    ).prefetch_related('options')

    answers = {
        ua.question_id: ua.selected_option_id
        for ua in UserAnswer.objects.filter(session=session)
    }

    result_data = []
    correct_count = 0

    for q in questions:
        correct_option = q.options.filter(is_correct=True).first()
        user_option_id = answers.get(q.id)

        is_correct = user_option_id == (correct_option.id if correct_option else None)
        if is_correct:
            correct_count += 1

        result_data.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "correct_option": correct_option.text if correct_option else "—",
            "user_option": (
                q.options.get(id=user_option_id).text
                if user_option_id and q.options.filter(id=user_option_id).exists()  # اطمینان از وجود گزینه
                else "بدون پاسخ"
            ),
            "is_correct": is_correct
        })

    return render(request, "team14/practice_result.html", {
        "session": session,
        "total_questions": questions.count(),
        "correct_count": correct_count,
        "results": result_data,
        "level": session.passage.get_difficulty_level_display()  # ✅ اینجا اصلاح شد
    })


@login_required(login_url='/auth/')
def start_exam(request):
    passages = Passage.objects.prefetch_related('questions__options').all()

    if not passages.exists():
        return redirect('index')

    passage = random.choice(list(passages))
    exam_duration = 30 * 60  # 1800 ثانیه

    session = UserSession.objects.create(
        user_id=str(request.user.id),
        passage=passage,
        mode='exam',
        start_time=timezone.now(),
        exam_duration=exam_duration
    )

    questions_qs = passage.questions.all().order_by('id')

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

    user_answers = {
        ans.question_id: ans.selected_option_id
        for ans in UserAnswer.objects.filter(session=session)
    }

    # محاسبه زمان باقی‌مانده (اگر session از قبل شروع شده)
    elapsed = (timezone.now() - session.start_time).total_seconds()
    time_left = max(0, exam_duration - int(elapsed))

    context = {
        'passage': passage,
        'questions': json.dumps(questions_data),
        'total_questions': questions_qs.count(),
        'session': session,
        'session_id': session.id,  # ✅ اضافه شد
        'user_answers': json.dumps(user_answers),
        'time_left': time_left,  # ✅ زمان دقیق
        'IS_EXAM': True,
    }

    return render(request, 'team14/exam.html', context)


@login_required(login_url='/auth/')
def exam_result(request, session_id):
    session = get_object_or_404(
        UserSession,
        id=session_id,
        user_id=str(request.user.id)
    )

    questions = Question.objects.filter(
        passage=session.passage
    ).prefetch_related('options')

    answers = {
        ua.question_id: ua.selected_option_id
        for ua in UserAnswer.objects.filter(session=session)
    }

    result_data = []
    correct_count = 0
    total_questions = questions.count()

    for q in questions:
        correct_option = q.options.filter(is_correct=True).first()
        user_option_id = answers.get(q.id)

        is_correct = user_option_id == (correct_option.id if correct_option else None)
        if is_correct:
            correct_count += 1

        result_data.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "correct_option": correct_option.text if correct_option else "—",
            "user_option": (
                q.options.get(id=user_option_id).text
                if user_option_id and q.options.filter(id=user_option_id).exists()
                else "بدون پاسخ"
            ),
            "is_correct": is_correct
        })

    # محاسبه نمره از 30
    score_out_of_30 = (correct_count / total_questions) * 30 if total_questions > 0 else 0
    percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    # ارزیابی براساس نمره
    if score_out_of_30 >= 20:
        evaluation_class = "evaluation-excellent"
        evaluation_title = "🎉 عالی!"
        evaluation_message = "شما در این آزمون عملکرد فوق‌العاده‌ای داشتید. مهارت خواندن شما در سطح بسیار خوبی است."
    elif score_out_of_30 >= 10:
        evaluation_class = "evaluation-good"
        evaluation_title = "👍 خوب"
        evaluation_message = "عملکرد خوبی داشتید. با تمرین بیشتر می‌توانید به نتایج بهتری برسید."
    else:
        evaluation_class = "evaluation-fair"
        evaluation_title = "💪 نیاز به تمرین"
        evaluation_message = "نگران نباشید! با تمرین مستمر و مطالعه بیشتر، مهارت شما بهبود خواهد یافت."

    # محاسبه مدت زمان
    if session.end_time and session.start_time:
        duration_seconds = (session.end_time - session.start_time).total_seconds()
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        duration = f"{minutes}:{seconds:02d}"
    else:
        duration = "—"

    # ذخیره نمره در session
    session.total_score = score_out_of_30
    session.save()
    wrong_count = total_questions - correct_count
    return render(request, "team14/exam_result.html", {
        "session": session,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "results": result_data,
        "level": session.passage.get_difficulty_level_display(),
        "percentage": percentage,
        "evaluation_class": evaluation_class,
        "evaluation_title": evaluation_title,
        "evaluation_message": evaluation_message,
        "duration": duration,
        "wrong_count": wrong_count,

    })


def finish_exam(request, session_id):
    session = get_object_or_404(
        UserSession,
        id=session_id,
        user_id=str(request.user.id),
        mode='exam'  # ✅ فقط آزمون
    )

    answers = UserAnswer.objects.filter(session=session)
    correct_count = 0

    for answer in answers:
        if answer.selected_option and answer.selected_option.is_correct:
            correct_count += 1
            answer.is_correct = True
        else:
            answer.is_correct = False
        answer.save()

    total_questions = session.passage.questions.count()

    if session.end_time is None:
        if total_questions > 0:
            # نمره از 30
            session.total_score = (correct_count / total_questions) * 30
        else:
            session.total_score = 0
        session.end_time = timezone.now()
        session.save()

    return redirect('exam_result', session_id=session.id)


def about(request):
    return None


def start_learning(request):
    return None
