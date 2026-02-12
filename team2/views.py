from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from functools import wraps
import os
from pathlib import Path

from core.auth import api_login_required
from team2.models import Lesson, UserDetails, VideoFiles

TEAM_NAME = "team2"


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
    return render(request, f"{TEAM_NAME}/index.html")

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
        Lesson,
        id=lesson_id,
        is_deleted=False,
        status='published'
    )

    videos = lesson.videos.filter(is_deleted=False).order_by('-uploaded_at')

    context = {
        'lesson': lesson,
        'videos': videos,
        'total_videos': videos.count(),
    }
    # TODO : create team2_lesson_details.html
    return render(request, 'team2_lesson_details.html', context)


@api_login_required
@teacher_required
@require_http_methods(["GET"])
def teacher_lessons_view(request):

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lessons = user_details.lessons.filter(is_deleted=False).prefetch_related('videos')
    except UserDetails.DoesNotExist:
        lessons = Lesson.objects.none()

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
        lesson = get_object_or_404(user_details.lessons.all(), id=lesson_id)
    except UserDetails.DoesNotExist:
        messages.error(request, 'پروفایل معلم یافت نشد.')
        return redirect('team2_teacher_lessons')

    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled')
        file_format = request.POST.get('file_format', 'mp4')
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
        lesson = get_object_or_404(user_details.lessons.all(), id=lesson_id)
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
