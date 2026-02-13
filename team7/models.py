import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class TaskType(models.TextChoices):
    WRITING = 'writing', _('Writing')
    SPEAKING = 'speaking', _('Speaking')

class Mode(models.TextChoices):
    INDEPENDENT = 'independent', _('Independent')
    INTEGRATED = 'integrated', _('Integrated')

# New Exam model to group questions and hold shared metadata
class Exam(models.Model):
    exam_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.WRITING)
    total_time = models.IntegerField(default=0, help_text="Total time for the exam in seconds")
    total_questions = models.IntegerField(default=0)
    difficulty = models.IntegerField(default=1)  # 1 to 5

    def __str__(self):
        return f"{self.title} ({self.get_exam_type_display()})"


class Question(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, help_text="Display title for the question")
    prompt_text = models.TextField()
    task_type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.WRITING)
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.INDEPENDENT)
    resource_url = models.CharField(max_length=500, blank=True, null=True)
    # difficulty moved to Exam; questions now reference an Exam
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    requirements = models.JSONField(default=list, blank=True, help_text="List of requirements/instructions for the task")
    tips = models.JSONField(default=list, blank=True, help_text="List of helpful tips for completing the task")

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.mode} ({self.question_id})"

class Evaluation(models.Model):
    evaluation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(help_text="Reference to Core User UUID")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='evaluations')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='evaluations', null=True, blank=True, help_text="Reference to Exam")
    task_type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.WRITING)
    
    # Inputs
    submitted_text = models.TextField(blank=True, null=True) # For Writing
    audio_path = models.CharField(max_length=500, blank=True, null=True) # For Speaking
    
    # Outputs
    overall_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    ai_feedback = models.TextField(blank=True, null=True)
    transcript_text = models.TextField(blank=True, null=True) # For Speaking ASR result
    rubric_version_id = models.CharField(max_length=50, blank=True, null=True, help_text="Track rubric version for scoring consistency")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user_id', '-created_at'])]

    def __str__(self):
        return f"Eval {self.evaluation_id} - {self.task_type} - Score: {self.overall_score}"

class DetailedScore(models.Model):
    score_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='detailed_scores')
    criterion = models.CharField(max_length=50) # e.g., 'Grammar', 'Vocabulary'
    score_value = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.criterion}: {self.score_value}"


class APILog(models.Model):
    """API request logging for monitoring and analytics (FR-MON, NFR-AVAIL-01).
    
    Tracks all API requests to monitor system health, performance,
    and identify bottlenecks or failures.
    """
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True, help_text="Reference to User UUID (null for unauthenticated)")
    endpoint = models.CharField(max_length=200, help_text="API endpoint path")
    method = models.CharField(max_length=10, default='GET', help_text="HTTP method")
    status_code = models.IntegerField(help_text="HTTP response status code")
    latency_ms = models.IntegerField(help_text="Request processing time in milliseconds")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Optional fields for detailed debugging
    error_message = models.TextField(blank=True, null=True, help_text="Error details if status >= 400")
    request_size = models.IntegerField(null=True, blank=True, help_text="Request body size in bytes")
    response_size = models.IntegerField(null=True, blank=True, help_text="Response body size in bytes")

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['status_code', '-timestamp']),
            models.Index(fields=['user_id', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.latency_ms}ms)"