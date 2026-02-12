from django.db import models
from django.conf import settings

# Test can be used in both practice and exam mode
MODE_CHOICES = [(1, 'Practice'), (2, 'Exam')]
DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]
ITEM_TYPE_CHOICES = [('lecture', 'Lecture'), ('conversation', 'Conversation')]
QUESTION_TYPE_CHOICES = [
    ('main_idea', 'Main Idea'),
    ('detail', 'Detail'),
    ('inference', 'Inference'),
    ('organization', 'Organization'),
    ('pragmatic', 'Pragmatic'),
]
SESSION_STATUS_CHOICES = [
    ('active', 'Active'),
    ('finished', 'Finished'),
    ('abandoned', 'Abandoned'),
]
EVENT_TYPE_CHOICES = [('focus_loss', 'Focus Loss'), ('replay', 'Replay')]


class ListeningTest(models.Model):
    title = models.CharField(max_length=255)
    version_id = models.CharField(max_length=64, blank=True)
    total_items = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ListeningItem(models.Model):
    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE, related_name='items')
    audio = models.FileField(upload_to='audio/%Y/%m/', blank=True, null=True)
    audio_url = models.URLField(max_length=500, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/', blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    topic_tag = models.CharField(max_length=100, blank=True)
    transcript = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='lecture')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['test', 'order']

    def __str__(self):
        return f"{self.get_item_type_display()} ({self.test.title})"

    @property
    def audio_source(self):
        return self.audio_url or (self.audio.url if self.audio else '')

    @property
    def thumbnail_source(self):
        if self.thumbnail_url:
            return self.thumbnail_url
        if self.thumbnail:
            return self.thumbnail.url
        return ''


class Question(models.Model):
    item = models.ForeignKey(ListeningItem, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='detail')
    score_weight = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True)

    class Meta:
        ordering = ['item', 'order']

    def __str__(self):
        return self.text[:80] + '...' if len(self.text) > 80 else self.text


class ChoiceOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=2)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['question', 'order']
        unique_together = [['question', 'label']]

    def __str__(self):
        return f"{self.label}: {self.text[:40]}..."


class ListeningSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listening_sessions'
    )
    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE, related_name='sessions')
    mode = models.CharField(max_length=20, choices=[('practice', 'Practice'), ('exam', 'Exam')])
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='active')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"Session {self.id} - {self.test.title} ({self.mode})"


class UserAnswer(models.Model):
    session = models.ForeignKey(ListeningSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    selected_option = models.ForeignKey(
        ChoiceOption, on_delete=models.CASCADE, related_name='+', null=True, blank=True
    )
    is_correct = models.BooleanField(null=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['session', 'question']]


class AntiCheatEvent(models.Model):
    session = models.ForeignKey(ListeningSession, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    occurred_at = models.DateTimeField(auto_now_add=True)
    count = models.PositiveIntegerField(default=1)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['occurred_at']


class ScoreReport(models.Model):
    session = models.OneToOneField(
        ListeningSession, on_delete=models.CASCADE, related_name='score_report'
    )
    total_score = models.PositiveIntegerField(default=0)
    main_idea = models.PositiveIntegerField(default=0)
    detail = models.PositiveIntegerField(default=0)
    inference = models.PositiveIntegerField(default=0)
    organization = models.PositiveIntegerField(default=0)
    pragmatic = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
