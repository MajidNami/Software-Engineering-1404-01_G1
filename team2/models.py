from django.db import models

class Lesson(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    id = models.BigAutoField(primary_key=True)
    teacher_id = models.UUIDField(db_index=True, null=True, blank=True)  # Reference to UserDetails with role='teacher'
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.CharField(max_length=255)
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )
    skill = models.CharField(max_length=255)
    duration_seconds = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
    )
    published_date = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class VideoFiles(models.Model):

    FORMAT_CHOICES = [
        ('mp4', 'MP4'),
        ('mkv', 'MKV'),
        ('avi', 'AVI'),
        ('mov', 'MOV'),
        ('webm', 'WebM'),
    ]

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='videos',
    )
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.BigIntegerField()
    file_format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
    )
    uploaded_at = models.DateTimeField()
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lesson.title} - {self.file_format}"

class UserDetails(models.Model):

    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    user_id = models.UUIDField(unique=True, db_index=True, null=True, blank=True)  # Reference to core.User.id بدون ForeignKey
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
        default='student'
    )

    lessons = models.ManyToManyField(
        Lesson,
        related_name='user_details_set',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.email} : {self.role}"


class Rating(models.Model):

    id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    user_id = models.UUIDField(db_index=True)  # Reference to core.User.id
    score = models.IntegerField(
        help_text='Score from 1 to 5'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['lesson', 'user_id']  # یک کاربر فقط یک امتیاز به هر درس
        indexes = [
            models.Index(fields=['lesson', 'user_id']),
            models.Index(fields=['lesson', 'score']),
        ]

    def __str__(self):
        return f"Rating {self.score}/5 for {self.lesson.title}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.score < 1 or self.score > 5:
            raise ValidationError('Score must be between 1 and 5')
