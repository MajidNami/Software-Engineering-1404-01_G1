from django.db import models
from django.contrib.auth import get_user_model
from .answer import UserSession

User = get_user_model()

class SkillScore(models.Model):
    SKILL_CHOICES = [
        ('main_idea', 'Main Idea'),
        ('supporting_detail', 'Supporting Detail'),
        ('inference', 'Inference'),
        ('vocabulary', 'Vocabulary'),
        ('cohesion', 'Cohesion'),
        ('organization', 'Organization'),
    ]

    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='skill_scores')
    skill_type = models.CharField(max_length=30, choices=SKILL_CHOICES)
    score = models.FloatField()

    def __str__(self):
        return f"{self.skill_type} - {self.score}"

class AntiCheatLog(models.Model):
    EVENT_CHOICES = [
        ('focus_lost', 'Focus Lost'),
        ('answer_changed', 'Answer Changed'),
        ('long_idle', 'Long Idle'),
    ]

    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='cheat_logs')
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)
