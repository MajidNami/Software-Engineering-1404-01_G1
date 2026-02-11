from django.db import models


class ListeningPracticeSession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        FINISHED = "FINISHED", "Finished"
        SUSPICIOUS = "SUSPICIOUS", "Suspicious"

    user_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)


class ListeningPracticeAnswer(models.Model):
    session = models.ForeignKey(
        ListeningPracticeSession, on_delete=models.CASCADE, related_name="answers"
    )
    question_number = models.IntegerField()
    selected_choice = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    time_spent_seconds = models.IntegerField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)


class ListeningEventLog(models.Model):
    class EventType(models.TextChoices):
        FOCUS_LOST = "FOCUS_LOST", "Focus lost"
        REPLAY = "REPLAY", "Replay"
        PAUSE = "PAUSE", "Pause"
        SEEK = "SEEK", "Seek"

    session = models.ForeignKey(
        ListeningPracticeSession, on_delete=models.CASCADE, null=True, blank=True
    )
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(null=True, blank=True)
