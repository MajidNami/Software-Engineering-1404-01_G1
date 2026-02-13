from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Passage(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    TOPIC_CHOICES = [
        ('biology', 'Biology'),
        ('history', 'History'),
        ('astronomy', 'Astronomy'),
        ('geology', 'Geology'),
        ('anthropology', 'Anthropology'),
    ]

    title = models.CharField(max_length=255)
    text = models.TextField()
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES)
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    text_length = models.IntegerField()
    rubric_version = models.CharField(max_length=50)
    version = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('factual', 'Factual Information'),
        ('negative_factual', 'Negative Factual'),
        ('inference', 'Inference'),
        ('vocabulary', 'Vocabulary in Context'),
        ('insert_sentence', 'Insert Sentence'),
        ('summary', 'Summary'),
        ('table', 'Table Completion'),
    ]

    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPE_CHOICES)
    correct_answer = models.TextField()
    score = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.question_type} - {self.passage.title}"

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:50]
