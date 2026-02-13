from django.db import models

from team13.models import base_models


class Question(base_models.TimeModel):
    """Assessment questions and their exemplar responses."""
    WRITING_QUESTION_TYPE = 'writing'
    SPEAKING_QUESTION_TYPE = 'speaking'
    QUESTION_TYPES = [(WRITING_QUESTION_TYPE, 'Writing'), (SPEAKING_QUESTION_TYPE, 'Speaking')]
    title = models.CharField(max_length=255)
    text = models.TextField()
    sample_correct_answer = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, db_index=True)
