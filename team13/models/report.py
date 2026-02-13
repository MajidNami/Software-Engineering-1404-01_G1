from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.db import models

from team13.models import base_models
from team13.models import question
from core.models import User


class ViewedQuestion(base_models.TimeModel):
    """Tracks which questions a user has viewed, regardless of submission status."""
    user_id = models.UUIDField()
    question = models.ForeignKey(question.Question, on_delete=models.CASCADE)


class BaseGradeResult(base_models.TimeModel):
    """Abstract base for all grading results. Stores overall score and links user/question."""
    user_id = models.UUIDField()
    question = models.ForeignKey(question.Question, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])

    class Meta:
        abstract = True


class WritingGradeResult(BaseGradeResult):
    """Stores detailed writing assessment scores across ETS TOEFL rubric categories."""
    task_achievement = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
    coherence = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
    vocabulary = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
    grammar = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
    mechanics = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])


class SpeakingGradeResult(BaseGradeResult):
    """Stores detailed speaking assessment scores across ETS TOEFL rubric categories."""
    delivery = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
    language_use = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
    topic_development = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
