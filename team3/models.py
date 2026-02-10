from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

# Custom choices/Enums
class ExamSection(models.TextChoices):
    LISTENING = 'listening', 'Listening'
    READING = 'reading', 'Reading'
    WRITING = 'writing', 'Writing'
    SPEAKING = 'speaking', 'Speaking'

class ExamSystem(models.TextChoices):
    IELTS = 'ielts', 'IELTS'
    TOEFL = 'toefl', 'TOEFL'
    GENERAL = 'general', 'General English'

class UserExamStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    IN_PROGRESS = 'in_progress', 'In Progress'
    SUBMITTED = 'submitted', 'Submitted'
    REVIEWED = 'reviewed', 'Reviewed'
    GRADED = 'graded', 'Graded'

class Exam(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    section = models.CharField(max_length=50,choices=ExamSection.choices,verbose_name='Exam Section')
    system = models.CharField(max_length=50, choices=ExamSystem.choices, verbose_name='Exam System')
    exam_time_seconds = models.PositiveIntegerField(
        validators=[MinValueValidator(60), MaxValueValidator(36000)],
        verbose_name='Exam Time (seconds)'
    )

    created_at = models.DateTimeField(default=timezone.now, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')

    class Meta:
        app_label = 'team3'
        db_table = 'exam'
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
        indexes = [
            models.Index(fields=['section', 'system']),
            models.Index(fields=['deleted_at']),
        ]

    def __str__(self):
        return f"{self.get_system_display()} - {self.get_section_display()} ({self.exam_time_seconds}s)"

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()


class Question(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE,related_name='questions',verbose_name='Exam')
    number = models.PositiveIntegerField(verbose_name='Question Number')
    description = models.TextField(verbose_name='Question Description')

    # Timestamps with soft delete
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')

    class Meta:
        app_label = 'team3'
        db_table = 'question'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        constraints = [
            models.UniqueConstraint(
                fields=['exam', 'number'],
                condition=models.Q(deleted_at__isnull=True),
                name='active_number_exam_question_uq'
            )
        ]
        indexes = [
            models.Index(fields=['exam', 'number']),
            models.Index(fields=['deleted_at']),
        ]

    def __str__(self):
        return f"Q{self.number}: {self.description[:50]}..."

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()


class Feedback(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    description = models.TextField(verbose_name='Feedback Description')

    # Timestamps with soft delete
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')

    class Meta:
        app_label = 'team3'
        db_table = 'feedback'
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        indexes = [
            models.Index(fields=['deleted_at']),
        ]

    def __str__(self):
        return f"Feedback #{self.id}: {self.description[:50]}..."

    def soft_delete(self):
        """Soft delete the feedback"""
        self.deleted_at = timezone.now()
        self.save()

class UserExam(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='user_exams',verbose_name='User')
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE,related_name='user_exams', verbose_name='Exam')
    attempt_no = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)],verbose_name='Attempt Number')
    status = models.CharField(max_length=20,choices=UserExamStatus.choices,default=UserExamStatus.DRAFT,verbose_name='Status')
    response_text = models.TextField(blank=True, null=True, verbose_name='Text Response')
    response_voice_path = models.CharField(max_length=500,    blank=True,null=True, verbose_name='Voice File Path')
    feedback = models.ForeignKey(Feedback, on_delete=models.SET_NULL,null=True,blank=True, related_name='user_exams',verbose_name='Feedback')

    # Timestamps with soft delete
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')

    class Meta:
        app_label = 'team3'
        db_table = 'user_exam'
        verbose_name = 'User Exam'
        verbose_name_plural = 'User Exams'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'exam', 'attempt_no'],
                condition=models.Q(deleted_at__isnull=True),
                name='active_attempt_exam_user_uq'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'exam']),
            models.Index(fields=['status'], name='ix_user_exam_status_active'),
            models.Index(fields=['deleted_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.exam} (Attempt #{self.attempt_no})"

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def get_next_attempt_number(self):
        last_attempt = UserExam.objects.filter(user=self.user, exam=self.exam, deleted_at__isnull=True).order_by('-attempt_no').first()
        if last_attempt:
            return last_attempt.attempt_no + 1
        return 1

    def save(self, *args, **kwargs):
        if not self.attempt_no:
            self.attempt_no = self.get_next_attempt_number()
        super().save(*args, **kwargs)
