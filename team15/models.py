from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    class Meta:
        abstract = True


class Test(SoftDeleteModel):
    MODE_CHOICES = [
        ("exam", "Exam"),
        ("practice", "Practice"),
    ]

    title = models.CharField(max_length=255)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    time_limit = models.IntegerField(help_text="Time limit in minutes, 0 for no limit", default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tests"

    def __str__(self):
        return f"{self.title} ({self.mode})"


class Passage(SoftDeleteModel):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="passages")
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "passages"
        ordering = ["order"]

    def __str__(self):
        return self.title


class Question(SoftDeleteModel):
    QUESTION_TYPES = [
        ("multiple_choice", "Multiple Choice"),
        ("insert_text", "Insert Text"),
    ]

    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default="multiple_choice")
    choices = models.JSONField(help_text='List of choices, e.g. ["A) ...", "B) ...", "C) ...", "D) ..."]')
    correct_answer = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "questions"
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class TestAttempt(SoftDeleteModel):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts")
    user_id = models.CharField(max_length=36, help_text="UUID of the user from core.User")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="in_progress")
    score = models.FloatField(null=True, blank=True)
    total_time = models.IntegerField(null=True, blank=True, help_text="Total time spent in seconds")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "test_attempts"

    def __str__(self):
        return f"Attempt by {self.user_id} on {self.test.title}"


class Answer(SoftDeleteModel):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    time_spent = models.IntegerField(null=True, blank=True, help_text="Time spent on this question in seconds")
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "answers"
        unique_together = [("attempt", "question")]

    def __str__(self):
        return f"Answer to Q{self.question.order} ({'correct' if self.is_correct else 'wrong'})"
