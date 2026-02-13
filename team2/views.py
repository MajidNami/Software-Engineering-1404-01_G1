from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.db import models
from functools import wraps
import os
import mimetypes
from pathlib import Path

from core.auth import api_login_required
from team2.models import Lesson, UserDetails, VideoFiles, Rating, Question, Answer, LessonView

TEAM_NAME = "team2"


def get_mime_type(file_path):

    if not file_path:
        return 'video/mp4'
    
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type:
        return mime_type
    
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        '.mp4': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.webm': 'video/webm',
        '.flv': 'video/x-flv',
        '.wmv': 'video/x-ms-wmv',
    }
    
    return mime_map.get(ext, 'video/mp4')


def format_file_size(size_bytes):

    if size_bytes >= 1073741824:
        return f"{size_bytes / 1073741824:.2f} GB"
    elif size_bytes >= 1048576:
        return f"{size_bytes / 1048576:.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


def teacher_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا ابتدا وارد شوید.')
            return redirect('auth')
        
        try:
            user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
            if user_details.role != 'teacher':
                messages.error(request, 'فقط معلم‌ها دسترسی به این صفحه دارند.')
                return redirect('team2_ping')
        except UserDetails.DoesNotExist:
            messages.error(request, 'پروفایل یافت نشد. لطفا با مدیر تماس بگیرید.')
            return redirect('team2_ping')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'فقط ادمین‌ها دسترسی به این صفحه دارند.')
            return redirect('team2_ping')
        return view_func(request, *args, **kwargs)
    return wrapper


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    """
    صفحه اصلی میکروسرویس
    """
    if not request.user.is_authenticated:
        return render(request, f"{TEAM_NAME}/index.html")

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        if user_details.role == 'teacher':
            return redirect('team2_teacher_home')
        else:
            return redirect('team2_student_home')
    except UserDetails.DoesNotExist:
        return render(request, f"{TEAM_NAME}/index.html")


@api_login_required
@require_http_methods(["GET"])
def student_home(request):
    """
    صفحه اصلی دانشجو با دروس، پیشرفت و سؤالات
    """
    from django.db.models import Count, Avg, Q

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)

        # دروس ثبت‌نامی
        enrolled_lessons = user_details.lessons.filter(
            is_deleted=False,
            status='published'
        ).order_by('-created_at')

        # آمار پیشرفت
        lessons_stats = []
        for lesson in enrolled_lessons:
            # پیشرفت تماشا
            view = LessonView.objects.using('team2').filter(
                lesson=lesson,
                user_id=request.user.id
            ).first()

            # امتیاز داده شده
            rating = Rating.objects.using('team2').filter(
                lesson=lesson,
                user_id=request.user.id,
                is_deleted=False
            ).first()

            lessons_stats.append({
                'lesson': lesson,
                'watch_time': (view.watch_duration_seconds // 60) if view else 0,
                'completed': view.completed if view else False,
                'my_rating': rating.score if rating else None,
            })

        # سؤالات پرسیده شده
        my_questions = Question.objects.using('team2').filter(
            user_id=request.user.id,
            is_deleted=False
        ).select_related('lesson').prefetch_related('answers').order_by('-created_at')[:5]

        # آمار کلی
        total_watch_time = LessonView.objects.using('team2').filter(
            user_id=request.user.id
        ).aggregate(total=models.Sum('watch_duration_seconds'))['total'] or 0

        completed_lessons = LessonView.objects.using('team2').filter(
            user_id=request.user.id,
            completed=True
        ).count()

        context = {
            'lessons_stats': lessons_stats,
            'total_lessons': enrolled_lessons.count(),
            'my_questions': my_questions,
            'total_questions': my_questions.count(),
            'total_watch_hours': round(total_watch_time / 3600, 1),
            'completed_lessons': completed_lessons,
        }

    except UserDetails.DoesNotExist:
        context = {
            'lessons_stats': [],
            'total_lessons': 0,
            'my_questions': [],
            'total_questions': 0,
            'total_watch_hours': 0,
            'completed_lessons': 0,
        }

    return render(request, 'team2_student_home.html', context)


@api_login_required
@teacher_required
@require_http_methods(["GET"])
def teacher_home(request):
    """
    صفحه اصلی معلم با دروس و آمار سریع
    """
    from django.db.models import Avg, Count, Sum, Q

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lessons = user_details.lessons.filter(is_deleted=False).order_by('-created_at')

        # آمار سریع برای هر درس
        lessons_quick_stats = []
        total_views = 0
        total_questions_unanswered = 0

        for lesson in lessons:
            views_count = LessonView.objects.using('team2').filter(lesson=lesson).count()
            total_views += views_count

            avg_rating = Rating.objects.using('team2').filter(
                lesson=lesson,
                is_deleted=False
            ).aggregate(avg=Avg('score'))['avg'] or 0

            questions_count = Question.objects.using('team2').filter(
                lesson=lesson,
                is_deleted=False
            ).count()

            unanswered_count = Question.objects.using('team2').filter(
                lesson=lesson,
                is_deleted=False,
                answers__isnull=True
            ).count()

            total_questions_unanswered += unanswered_count

            lessons_quick_stats.append({
                'lesson': lesson,
                'views': views_count,
                'avg_rating': round(avg_rating, 1),
                'questions': questions_count,
                'unanswered': unanswered_count,
            })

        # سؤالات اخیر بدون پاسخ
        recent_unanswered = Question.objects.using('team2').filter(
            lesson__in=lessons,
            is_deleted=False,
            answers__isnull=True
        ).select_related('lesson').order_by('-created_at')[:5]

        context = {
            'lessons_stats': lessons_quick_stats,
            'total_lessons': lessons.count(),
            'total_views': total_views,
            'total_unanswered': total_questions_unanswered,
            'recent_unanswered': recent_unanswered,
        }

    except UserDetails.DoesNotExist:
        context = {
            'lessons_stats': [],
            'total_lessons': 0,
            'total_views': 0,
            'total_unanswered': 0,
            'recent_unanswered': [],
        }

    return render(request, 'team2_teacher_home.html', context)

@api_login_required
@require_http_methods(["GET"])
def lessons_list_view(request):
    from team2.models import UserDetails
    
    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lessons = user_details.lessons.filter(
            is_deleted=False,
            status='published'
        ).prefetch_related('videos')
    except UserDetails.DoesNotExist:
        lessons = Lesson.objects.none()

    context = {
        'lessons': lessons,
        'total_lessons': lessons.count(),
    }

    return render(request, 'team2_Lessons_list.html', context)

@api_login_required
@require_http_methods(["GET"])
def lesson_details_view(request, lesson_id):

    lesson = get_object_or_404(
        Lesson.objects.using('team2'),
        id=lesson_id,
        is_deleted=False,
        status='published'
    )

    videos = lesson.videos.filter(is_deleted=False).order_by('-uploaded_at')
    
    # اضافه کردن اندازه فرمت شده به هر ویدیو
    for video in videos:
        video.formatted_size = format_file_size(video.file_size)

    context = {
        'lesson': lesson,
        'videos': videos,
        'total_videos': videos.count(),
    }
    return render(request, 'team2_lesson_details.html', context)


@api_login_required
@teacher_required
@require_http_methods(["GET"])
def teacher_lessons_view(request):

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        # فقط کلاس‌هایی که معلم ساخته است
        lessons = Lesson.objects.using('team2').filter(
            creator=user_details,
            is_deleted=False
        ).prefetch_related('videos')
    except UserDetails.DoesNotExist:
        lessons = Lesson.objects.using('team2').none()

    context = {
        'lessons': lessons,
        'total_lessons': lessons.count(),
    }
    return render(request, 'team2_teacher_lessons.html', context)

@api_login_required
@teacher_required
@require_http_methods(["GET", "POST"])
def add_video_view(request, lesson_id):

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lesson = get_object_or_404(Lesson.objects.using('team2'), id=lesson_id, is_deleted=False)
        
        if lesson.creator != user_details:
            messages.error(request, 'شما فقط می‌توانید در کلاس‌هایی که خودتان ساخته‌اید ویدیو اضافه کنید.')
            return redirect('team2_teacher_lessons')
            
    except UserDetails.DoesNotExist:
        messages.error(request, 'پروفایل معلم یافت نشد.')
        return redirect('team2_teacher_lessons')

    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled')
        video_file = request.FILES.get('video_file')

        if not video_file:
            messages.error(request, 'لطفا یک فایل ویدیو انتخاب کنید.')
            return render(request, 'team2_add_video.html', {'lesson': lesson})

        try:
            video_dir = os.path.join(settings.MEDIA_ROOT, 'team2', 'videos')
            Path(video_dir).mkdir(parents=True, exist_ok=True)
            
            import uuid
            file_name = f"{uuid.uuid4()}_{video_file.name}"
            file_path = os.path.join(video_dir, file_name)
            
            with open(file_path, 'wb+') as f:
                for chunk in video_file.chunks():
                    f.write(chunk)
            
            relative_path = os.path.join('team2', 'videos', file_name).replace('\\', '/')
            
            file_extension = os.path.splitext(video_file.name)[1].lower().lstrip('.')
            format_map = {
                'mp4': 'mp4',
                'mkv': 'mkv',
                'avi': 'avi',
                'mov': 'mov',
                'webm': 'webm',
            }
            file_format = format_map.get(file_extension, 'mp4')
            
            file_size = video_file.size
            video = VideoFiles.objects.using('team2').create(
                lesson=lesson,
                file_path=relative_path,
                file_format=file_format,
                file_size=file_size,
                uploaded_at=__import__('django.utils.timezone', fromlist=['now']).now(),
            )
            messages.success(request, f'ویدیو "{title}" با موفقیت آپلود شد.')
            return redirect('teacher_lesson_videos', lesson_id=lesson_id)
        except Exception as e:
            messages.error(request, f'خطا در آپلود ویدیو: {str(e)}')
            return render(request, 'team2_add_video.html', {'lesson': lesson})

    context = {
        'lesson': lesson,
    }
    return render(request, 'team2_add_video.html', context)



@api_login_required
@teacher_required
@require_http_methods(["GET"])
def teacher_lesson_videos_view(request, lesson_id):

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lesson = get_object_or_404(Lesson.objects.using('team2'), id=lesson_id, is_deleted=False)
        
        if lesson.creator != user_details:
            messages.error(request, 'شما فقط می‌توانید کلاس‌هایی که خودتان ساخته‌اید را مدیریت کنید.')
            return redirect('team2_teacher_lessons')
            
    except UserDetails.DoesNotExist:
        messages.error(request, 'پروفایل معلم یافت نشد.')
        return redirect('team2_teacher_lessons')

    videos = lesson.videos.all().order_by('-created_at')

    context = {
        'lesson': lesson,
        'videos': videos,
        'total_videos': videos.count(),
    }
    return render(request, 'team2_teacher_lesson_videos.html', context)



@api_login_required
@admin_required
@require_http_methods(["GET"])
def admin_users_view(request):
    users = UserDetails.objects.using('team2').all().order_by('-email')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'teachers_count': users.filter(role='teacher').count(),
        'students_count': users.filter(role='student').count(),
    }
    return render(request, 'team2_admin_users.html', context)



@api_login_required
@admin_required
@require_http_methods(["GET", "POST"])
def admin_change_role_view(request, user_id):
    
    user = get_object_or_404(UserDetails.objects.using('team2'), id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['teacher', 'student']:
            user.role = new_role
            user.save(using='team2')
            messages.success(request, f'نقش کاربر {user.email} به {new_role} تغییر یافت.')
            return redirect('admin_users')
        else:
            messages.error(request, 'نقش معتبر نیست.')
    
    context = {
        'user': user,
        'roles': [('teacher', 'معلم'), ('student', 'دانش‌جو')],
    }
    return render(request, 'team2_admin_change_role.html', context)


@api_login_required
@teacher_required
@require_http_methods(["GET", "POST"])
def teacher_create_lesson_view(request):

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        subject = request.POST.get('subject', '').strip()
        level = request.POST.get('level', 'beginner')
        skill = request.POST.get('skill', '').strip()
        duration = request.POST.get('duration', 0)
        
        if not all([title, description, subject, skill]):
            messages.error(request, 'تمام فیلدها الزامی هستند.')
            return redirect('teacher_create_lesson')
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            messages.error(request, 'سطح معتبر نیست.')
            return redirect('teacher_create_lesson')
        
        try:
            duration_seconds = int(duration) if duration else 0
            
            lesson = Lesson.objects.using('team2').create(
                title=title,
                description=description,
                subject=subject,
                level=level,
                skill=skill,
                duration_seconds=duration_seconds,
                status='draft',
            )
            
            try:
                user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
                lesson.creator = user_details
                lesson.save(using='team2')
                user_details.lessons.add(lesson)
            except UserDetails.DoesNotExist:
                pass
            
            messages.success(request, f'درس "{title}" با موفقیت ساخته شد.')
            return redirect('team2_teacher_lessons')
        except Exception as e:
            messages.error(request, f'خطا در ساخت درس: {str(e)}')
    
    context = {
        'levels': [('beginner', 'مبتدی'), ('intermediate', 'متوسط'), ('advanced', 'پیشرفته')],
    }
    return render(request, 'team2_teacher_create_lesson.html', context)


@api_login_required
@require_http_methods(["GET"])
def watch_video_view(request, lesson_id, video_id):

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lesson = Lesson.objects.using('team2').get(id=lesson_id, is_deleted=False)
        
        is_creator = lesson.creator == user_details
        is_enrolled = lesson in user_details.lessons.all()
        
        if not (is_creator or is_enrolled):
            messages.error(request, 'شما در این درس ثبت‌نام نکرده‌اید')
            return redirect('browse_lessons')
        
        video = VideoFiles.objects.using('team2').get(
            id=video_id, 
            lesson_id=lesson_id, 
            is_deleted=False
        )
        
        all_videos = VideoFiles.objects.using('team2').filter(
            lesson_id=lesson_id, 
            is_deleted=False
        ).order_by('created_at')
        
        videos_list = list(all_videos)
        current_index = next((i for i, v in enumerate(videos_list) if v.id == video_id), None)
        
        previous_video = videos_list[current_index - 1] if current_index and current_index > 0 else None
        next_video = videos_list[current_index + 1] if current_index is not None and current_index < len(videos_list) - 1 else None
        
        video_mime_type = get_mime_type(video.file_path) if video.file_path else 'video/mp4'
        
        context = {
            'lesson': lesson,
            'video': video,
            'all_videos': all_videos,
            'previous_video': previous_video,
            'next_video': next_video,
            'current_video_index': current_index + 1 if current_index is not None else 1,
            'total_videos': len(videos_list),
            'video_mime_type': video_mime_type,
        }
        return render(request, 'team2_watch_video.html', context)
    
    except UserDetails.DoesNotExist:
        messages.error(request, 'لطفاً ابتدا درس را انتخاب کنید')
        return redirect('browse_lessons')
    except Lesson.DoesNotExist:
        messages.error(request, 'این درس پیدا نشد')
        return redirect('browse_lessons')
    except VideoFiles.DoesNotExist:
        messages.error(request, 'این ویدیو پیدا نشد')
        return redirect('student_lesson_videos', lesson_id=lesson_id)

@api_login_required
@require_http_methods(["GET"])
def browse_lessons_view(request):

    lessons = Lesson.objects.using('team2').filter(
        is_deleted=False,
        status='published'
    ).prefetch_related('videos')

    context = {
        'lessons': lessons,
        'total_lessons': lessons.count(),
    }
    return render(request, 'team2_browse_lessons.html', context)


@api_login_required
@require_http_methods(["GET", "POST"])
def enroll_lesson_view(request, lesson_id):

    if request.method == 'POST':
        try:
            user_details, _ = UserDetails.objects.using('team2').get_or_create(
                user_id=request.user.id,
                defaults={
                    'email': request.user.email,
                    'role': 'student',
                }
            )
            
            lesson = get_object_or_404(
                Lesson.objects.using('team2'),
                id=lesson_id,
                is_deleted=False,
                status='published'
            )
            
            if lesson not in user_details.lessons.all():
                user_details.lessons.add(lesson)
                messages.success(request, f'کلاس "{lesson.title}" با موفقیت به کلاس‌های شما اضافه شد.')
            else:
                messages.info(request, 'شما قبلاً در این کلاس ثبت‌نام کرده‌اید.')
            
            return redirect('team2_index')
        except Exception as e:
            messages.error(request, f'خطا در ثبت‌نام: {str(e)}')
            return redirect('browse_lessons')


@api_login_required
@require_http_methods(["GET"])
def student_lesson_videos_view(request, lesson_id):

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lesson = get_object_or_404(user_details.lessons.all(), id=lesson_id)
    except UserDetails.DoesNotExist:
        messages.error(request, 'پروفایل دانش‌آموز یافت نشد.')
        return redirect('browse_lessons')

    videos = lesson.videos.filter(is_deleted=False).order_by('-uploaded_at')

    context = {
        'lesson': lesson,
        'videos': videos,
        'total_videos': videos.count(),
    }
    return render(request, 'team2_student_lesson_videos.html', context)

    
@api_login_required
@teacher_required
@require_http_methods(["POST"])
def publish_lesson_view(request, lesson_id):
    
    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lesson = get_object_or_404(Lesson.objects.using('team2'), id=lesson_id, is_deleted=False)
        
        if lesson.creator != user_details:
            messages.error(request, 'شما فقط می‌توانید کلاس‌هایی که خودتان ساخته‌اید را منتشر کنید.')
            return redirect('team2_teacher_lessons')
        
        if not lesson.videos.filter(is_deleted=False).exists():
            messages.error(request, 'برای پابلیش درس باید حداقل یک ویدیو اضافه کنید.')
            return redirect('team2_teacher_lessons')
        
        from django.utils import timezone
        lesson.status = 'published'
        lesson.published_date = timezone.now()
        lesson.save(using='team2')
        
        messages.success(request, f'درس "{lesson.title}" با موفقیت منتشر شد.')
        return redirect('team2_teacher_lessons')
    
    except UserDetails.DoesNotExist:
        messages.error(request, 'پروفایل معلم یافت نشد.')
        return redirect('team2_teacher_lessons')
    except Lesson.DoesNotExist:
        messages.error(request, 'این درس پیدا نشد.')
        return redirect('team2_teacher_lessons')
    except Exception as e:
        messages.error(request, f'خطا در انتشار درس: {str(e)}')
        return redirect('team2_teacher_lessons')

@api_login_required
@require_http_methods(["POST"])
def rate_lesson_api(request, lesson_id):
    """
    POST /team2/api/lessons/<lesson_id>/rate/
    Body: {"score": 1-5}
    """
    import json
    from django.db import IntegrityError

    lesson = get_object_or_404(Lesson, id=lesson_id, is_deleted=False, status='published')

    # بررسی اینکه آیا کاربر در این درس ثبت‌نام کرده یا نه
    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        if not user_details.lessons.filter(id=lesson_id).exists():
            return JsonResponse({
                'error': 'شما در این درس ثبت‌نام نکرده‌اید. فقط شرکت‌کنندگان می‌توانند امتیاز دهند.'
            }, status=403)
    except UserDetails.DoesNotExist:
        return JsonResponse({'error': 'پروفایل کاربری یافت نشد'}, status=404)

    try:
        data = json.loads(request.body)
        score = int(data.get('score', 0))

        if score < 1 or score > 5:
            return JsonResponse({'error': 'امتیاز باید بین 1 تا 5 باشد'}, status=400)

        rating, created = Rating.objects.using('team2').update_or_create(
            lesson=lesson,
            user_id=request.user.id,
            defaults={'score': score}
        )


        from django.db.models import Avg
        avg_rating = Rating.objects.using('team2').filter(
            lesson=lesson,
            is_deleted=False
        ).aggregate(Avg('score'))['score__avg']

        return JsonResponse({
            'success': True,
            'message': 'با موفقیت ثبت شد' if created else 'امتیاز به‌روزرسانی شد',
            'rating': {
                'id': rating.id,
                'score': rating.score,
                'created': created
            },
            'lesson_avg_rating': round(avg_rating, 2) if avg_rating else 0,
            'total_ratings': Rating.objects.using('team2').filter(lesson=lesson, is_deleted=False).count()
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت JSON نامعتبر است'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'امتیاز باید عدد باشد'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_login_required
@require_http_methods(["GET"])
def lesson_ratings_api(request, lesson_id):
    """
    API endpoint برای دریافت امتیازهای یک درس
    GET /team2/api/lessons/<lesson_id>/ratings/
    """
    from django.db.models import Avg, Count

    lesson = get_object_or_404(Lesson, id=lesson_id, is_deleted=False)

    ratings = Rating.objects.using('team2').filter(
        lesson=lesson,
        is_deleted=False
    ).order_by('-created_at')


    stats = ratings.aggregate(
        avg_score=Avg('score'),
        total=Count('id')
    )


    distribution = {}
    for i in range(1, 6):
        distribution[f'star_{i}'] = ratings.filter(score=i).count()

  
    user_rating = None
    try:
        user_rating_obj = ratings.get(user_id=request.user.id)
        user_rating = user_rating_obj.score
    except Rating.DoesNotExist:
        pass

    return JsonResponse({
        'lesson_id': lesson.id,
        'lesson_title': lesson.title,
        'stats': {
            'average': round(stats['avg_score'], 2) if stats['avg_score'] else 0,
            'total': stats['total'],
            'distribution': distribution
        },
        'user_rating': user_rating,
        'ratings': [
            {
                'id': r.id,
                'score': r.score,
                'created_at': r.created_at.isoformat(),
            }
            for r in ratings[:10]  
        ]
    })


@api_login_required
@require_http_methods(["GET"])
def lessons_with_rating_view(request):
    """
    صفحه نمایش دروس با قابلیت امتیازدهی
    فقط دروسی که کاربر در آن‌ها ثبت‌نام کرده
    """
    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        # فقط دروسی که user در آن‌ها ثبت‌نام کرده
        lessons = user_details.lessons.filter(
            is_deleted=False,
            status='published'
        ).order_by('-created_at')
    except UserDetails.DoesNotExist:
        lessons = Lesson.objects.none()

    context = {
        'lessons': lessons,
    }
    return render(request, 'team2_lessons_with_rating.html', context)




@api_login_required
@require_http_methods(["POST"])
def ask_question_api(request, lesson_id):
    """
    API برای ثبت سؤال جدید
    POST /team2/api/lessons/<lesson_id>/ask/
    Body: {"question_text": "متن سؤال"}
    """
    import json

    lesson = get_object_or_404(Lesson, id=lesson_id, is_deleted=False, status='published')

    # بررسی اینکه کاربر در این درس ثبت‌نام کرده یا نه
    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        if not user_details.lessons.filter(id=lesson_id).exists():
            return JsonResponse({
                'error': 'شما در این درس ثبت‌نام نکرده‌اید. فقط شرکت‌کنندگان می‌توانند سؤال بپرسند.'
            }, status=403)
    except UserDetails.DoesNotExist:
        return JsonResponse({'error': 'پروفایل کاربری یافت نشد'}, status=404)

    try:
        data = json.loads(request.body)
        question_text = data.get('question_text', '').strip()

        if not question_text:
            return JsonResponse({'error': 'متن سؤال نمی‌تواند خالی باشد'}, status=400)

        if len(question_text) < 10:
            return JsonResponse({'error': 'متن سؤال باید حداقل 10 کاراکتر باشد'}, status=400)

        question = Question.objects.using('team2').create(
            lesson=lesson,
            user_id=request.user.id,
            question_text=question_text
        )

        return JsonResponse({
            'success': True,
            'message': 'سؤال با موفقیت ثبت شد',
            'question': {
                'id': question.id,
                'question_text': question.question_text,
                'created_at': question.created_at.isoformat(),
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت JSON نامعتبر است'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_login_required
@require_http_methods(["POST"])
def answer_question_api(request, question_id):
    """
    API برای پاسخ دادن به سؤال (فقط معلم)
    POST /team2/api/questions/<question_id>/answer/
    Body: {"answer_text": "متن پاسخ"}
    """
    import json

    question = get_object_or_404(Question, id=question_id, is_deleted=False)

    # بررسی اینکه کاربر معلم این درس است یا نه
    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        if user_details.role != 'teacher':
            return JsonResponse({'error': 'فقط معلمان می‌توانند پاسخ دهند'}, status=403)

        # بررسی اینکه معلم صاحب این درس است
        if not user_details.lessons.filter(id=question.lesson.id).exists():
            return JsonResponse({'error': 'شما معلم این درس نیستید'}, status=403)

    except UserDetails.DoesNotExist:
        return JsonResponse({'error': 'پروفایل کاربری یافت نشد'}, status=404)

    try:
        data = json.loads(request.body)
        answer_text = data.get('answer_text', '').strip()

        if not answer_text:
            return JsonResponse({'error': 'متن پاسخ نمی‌تواند خالی باشد'}, status=400)

        if len(answer_text) < 5:
            return JsonResponse({'error': 'متن پاسخ باید حداقل 5 کاراکتر باشد'}, status=400)

        answer = Answer.objects.using('team2').create(
            question=question,
            user_id=request.user.id,
            answer_text=answer_text
        )

        return JsonResponse({
            'success': True,
            'message': 'پاسخ با موفقیت ثبت شد',
            'answer': {
                'id': answer.id,
                'answer_text': answer.answer_text,
                'created_at': answer.created_at.isoformat(),
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت JSON نامعتبر است'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_login_required
@require_http_methods(["GET"])
def lesson_questions_api(request, lesson_id):
    """
    API برای دریافت لیست سؤالات و پاسخ‌های یک درس
    GET /team2/api/lessons/<lesson_id>/questions/
    """
    lesson = get_object_or_404(Lesson, id=lesson_id, is_deleted=False)

    questions = Question.objects.using('team2').filter(
        lesson=lesson,
        is_deleted=False
    ).order_by('-created_at').prefetch_related('answers')

    questions_data = []
    for q in questions:
        answers_data = [
            {
                'id': a.id,
                'answer_text': a.answer_text,
                'created_at': a.created_at.isoformat(),
                'is_teacher': True  # همه پاسخ‌ها از طرف معلم هستند
            }
            for a in q.answers.filter(is_deleted=False).order_by('created_at')
        ]

        questions_data.append({
            'id': q.id,
            'question_text': q.question_text,
            'created_at': q.created_at.isoformat(),
            'is_mine': q.user_id == request.user.id,
            'answers': answers_data,
            'answers_count': len(answers_data)
        })

    return JsonResponse({
        'lesson_id': lesson.id,
        'lesson_title': lesson.title,
        'total_questions': len(questions_data),
        'questions': questions_data
    })



@api_login_required
@require_http_methods(["POST"])
def track_view_api(request, lesson_id):
    """API برای ثبت بازدید و مدت زمان تماشا 
    POST /team2/api/lessons/<lesson_id>/track-view/
    Body: {"watch_duration": 120, "completed": false}
    """
    import json

    lesson = get_object_or_404(Lesson, id=lesson_id, is_deleted=False, status='published')

    try:
        data = json.loads(request.body)
        watch_duration = int(data.get('watch_duration', 0))
        completed = bool(data.get('completed', False))

        if watch_duration < 0:
            return JsonResponse({'error': 'زمان تماشا نمی‌تواند منفی باشد'}, status=400)

        # بروزرسانی یا ایجاد رکورد بازدید
        view, created = LessonView.objects.using('team2').get_or_create(
            lesson=lesson,
            user_id=request.user.id,
            defaults={
                'watch_duration_seconds': watch_duration,
                'completed': completed
            }
        )

        if not created:
            # اگر رکورد قبلاً وجود داشته، زمان تماشا را افزایش بده
            view.watch_duration_seconds = max(view.watch_duration_seconds, watch_duration)
            view.completed = completed or view.completed
            view.save(using='team2')

        return JsonResponse({
            'success': True,
            'message': 'بازدید ثبت شد',
            'view': {
                'id': view.id,
                'watch_duration': view.watch_duration_seconds,
                'completed': view.completed,
                'created': created
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت JSON نامعتبر است'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'مقادیر ورودی نامعتبر هستند'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_login_required
@teacher_required
@require_http_methods(["GET"])
def teacher_lesson_stats_api(request, lesson_id):
    """
    API برای دریافت آمار یک درس توسط معلم
    GET /team2/api/teacher/lessons/<lesson_id>/stats/
    """
    from django.db.models import Avg, Sum, Count

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lesson = get_object_or_404(user_details.lessons.all(), id=lesson_id, is_deleted=False)
    except UserDetails.DoesNotExist:
        return JsonResponse({'error': 'پروفایل معلم یافت نشد'}, status=404)

    # آمار بازدید
    views = LessonView.objects.using('team2').filter(lesson=lesson)
    views_stats = views.aggregate(
        total_views=Count('id'),
        total_watch_time=Sum('watch_duration_seconds'),
        avg_watch_time=Avg('watch_duration_seconds'),
        completed_count=Count('id', filter=models.Q(completed=True))
    )

    # آمار امتیازات
    ratings = Rating.objects.using('team2').filter(lesson=lesson, is_deleted=False)
    ratings_stats = ratings.aggregate(
        avg_rating=Avg('score'),
        total_ratings=Count('id')
    )

    # توزیع امتیاز
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[f'star_{i}'] = ratings.filter(score=i).count()

    # آمار سؤالات
    questions = Question.objects.using('team2').filter(lesson=lesson, is_deleted=False)
    questions_stats = {
        'total_questions': questions.count(),
        'answered_questions': questions.filter(answers__is_deleted=False).distinct().count(),
        'unanswered_questions': questions.filter(answers__isnull=True).count()
    }

    # میانگین زمان تماشا در دقیقه
    avg_watch_minutes = (views_stats['avg_watch_time'] or 0) / 60
    total_watch_hours = (views_stats['total_watch_time'] or 0) / 3600

    # نرخ تکمیل
    completion_rate = 0
    if views_stats['total_views'] > 0:
        completion_rate = (views_stats['completed_count'] / views_stats['total_views']) * 100

    return JsonResponse({
        'lesson': {
            'id': lesson.id,
            'title': lesson.title,
            'status': lesson.status,
            'level': lesson.level,
            'skill': lesson.skill
        },
        'views': {
            'total': views_stats['total_views'],
            'completed': views_stats['completed_count'],
            'completion_rate': round(completion_rate, 2),
            'total_watch_hours': round(total_watch_hours, 2),
            'avg_watch_minutes': round(avg_watch_minutes, 2)
        },
        'ratings': {
            'average': round(ratings_stats['avg_rating'], 2) if ratings_stats['avg_rating'] else 0,
            'total': ratings_stats['total_ratings'],
            'distribution': rating_distribution
        },
        'questions': questions_stats
    })


@api_login_required
@teacher_required
@require_http_methods(["GET"])
def teacher_dashboard_view(request):

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lessons = user_details.lessons.filter(is_deleted=False).order_by('-created_at')
    except UserDetails.DoesNotExist:
        lessons = Lesson.objects.none()

    from django.db.models import Avg, Count, Sum

    lessons_stats = []
    for lesson in lessons:
        # آمار بازدید
        views_count = LessonView.objects.using('team2').filter(lesson=lesson).count()
        total_watch = LessonView.objects.using('team2').filter(lesson=lesson).aggregate(
            total=Sum('watch_duration_seconds')
        )['total'] or 0

        # آمار امتیازات
        ratings = Rating.objects.using('team2').filter(lesson=lesson, is_deleted=False)
        avg_rating = ratings.aggregate(avg=Avg('score'))['avg'] or 0
        ratings_count = ratings.count()

        # آمار سؤالات
        questions_count = Question.objects.using('team2').filter(
            lesson=lesson, is_deleted=False
        ).count()

        lessons_stats.append({
            'lesson': lesson,
            'views_count': views_count,
            'total_watch_hours': round(total_watch / 3600, 2),
            'avg_rating': round(avg_rating, 2),
            'ratings_count': ratings_count,
            'questions_count': questions_count
        })

    context = {
        'lessons_stats': lessons_stats,
        'total_lessons': lessons.count()
    }
    return render(request, 'team2_teacher_dashboard.html', context)
