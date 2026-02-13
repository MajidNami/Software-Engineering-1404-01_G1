from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from functools import wraps
import os
import mimetypes
from pathlib import Path

from core.auth import api_login_required
from team2.models import Lesson, UserDetails, VideoFiles

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

    if not request.user.is_authenticated:
        available_lessons = Lesson.objects.using('team2').filter(
            is_deleted=False,
            status='published'
        ).prefetch_related('videos')
        return render(request, f"{TEAM_NAME}/index.html", {
            'is_authenticated': False,
            'lessons': [],
            'is_teacher': False,
            'available_lessons': available_lessons,
            'total_available': available_lessons.count(),
        })
    
    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
    except UserDetails.DoesNotExist:

        user_details = UserDetails.objects.using('team2').create(
            user_id=request.user.id,
            email=request.user.email,
            role='student'
        )
    
    is_teacher = user_details.role == 'teacher'
    
    # اگر معلم است، هم کلاس‌هایی که خودش ساخته و هم کلاس‌هایی که در آن‌ها ثبت‌نام کرده را نشان بده
    # اگر دانش‌آموز است، فقط کلاس‌هایی که در آن‌ها ثبت‌نام کرده را نشان بده
    if is_teacher:
        # کلاس‌هایی که معلم ساخته
        created_lessons = Lesson.objects.using('team2').filter(
            creator=user_details,
            is_deleted=False
        )
        # کلاس‌هایی که معلم در آن‌ها ثبت‌نام کرده (به عنوان دانش‌آموز)
        enrolled_lessons = user_details.lessons.filter(
            is_deleted=False,
            status='published'
        ).exclude(creator=user_details)  # کلاس‌هایی که خودش نساخته
        
        # ترکیب هر دو
        from django.db.models import Q
        lessons = Lesson.objects.using('team2').filter(
            Q(id__in=created_lessons.values_list('id', flat=True)) |
            Q(id__in=enrolled_lessons.values_list('id', flat=True)),
            is_deleted=False
        ).distinct().prefetch_related('videos')
    else:
        lessons = user_details.lessons.filter(
            is_deleted=False,
            status='published'
        ).prefetch_related('videos')
    
    # کلاس‌های منتشر شده که کاربر در آن‌ها ثبت‌نام نکرده
    enrolled_lesson_ids = user_details.lessons.values_list('id', flat=True)
    available_lessons = Lesson.objects.using('team2').filter(
        is_deleted=False,
        status='published'
    ).exclude(id__in=enrolled_lesson_ids).prefetch_related('videos')
    
    context = {
        'is_authenticated': True,
        'lessons': lessons,
        'is_teacher': is_teacher,
        'total_lessons': lessons.count(),
        'user_details': user_details,  # برای بررسی creator در تمپلیت
        'available_lessons': available_lessons,  # کلاس‌های منتشر شده برای ثبت‌نام
        'total_available': available_lessons.count(),
    }
    return render(request, f"{TEAM_NAME}/index.html", context)

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
