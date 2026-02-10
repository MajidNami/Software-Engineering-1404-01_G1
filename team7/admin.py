from django.contrib import admin
from .models import Question, Evaluation, DetailedScore, APILog


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin panel for question management (FR-MON)."""
    list_display = ('question_id', 'task_type', 'mode', 'difficulty')
    list_filter = ('task_type', 'mode', 'difficulty')
    search_fields = ('prompt_text',)
    readonly_fields = ('question_id',)

    fieldsets = (
        ('Question Info', {
            'fields': ('question_id', 'prompt_text', 'task_type', 'mode')
        }),
        ('Metadata', {
            'fields': ('difficulty', 'resource_url')
        }),
    )


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """Admin panel for evaluation monitoring (FR-MON, UC-04)."""
    list_display = ('evaluation_id', 'user_id', 'task_type', 'overall_score', 'created_at')
    list_filter = ('task_type', 'created_at')
    search_fields = ('user_id', 'evaluation_id')
    readonly_fields = ('evaluation_id', 'user_id', 'question', 'created_at', 'rubric_version_id')

    fieldsets = (
        ('Evaluation Info', {
            'fields': ('evaluation_id', 'user_id', 'question', 'task_type')
        }),
        ('Submission Data', {
            'fields': ('submitted_text', 'audio_path', 'transcript_text')
        }),
        ('Scoring', {
            'fields': ('overall_score', 'ai_feedback', 'rubric_version_id')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation; only system creates evaluations."""
        return False


@admin.register(DetailedScore)
class DetailedScoreAdmin(admin.ModelAdmin):
    """Admin panel for detailed criterion scores."""
    list_display = ('score_id', 'evaluation', 'criterion', 'score_value')
    list_filter = ('criterion', 'evaluation__created_at')
    search_fields = ('evaluation__evaluation_id', 'criterion')
    readonly_fields = ('score_id', 'evaluation')

    fieldsets = (
        ('Score Info', {
            'fields': ('score_id', 'evaluation', 'criterion', 'score_value')
        }),
        ('Feedback', {
            'fields': ('comment',)
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation; only system creates scores."""
        return False


@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    """Admin panel for API logging and monitoring (UC-04, FR-MON)."""
    list_display = ('log_id', 'endpoint', 'method', 'status_code', 'latency_ms', 'user_id', 'timestamp')
    list_filter = ('method', 'status_code', 'timestamp')
    search_fields = ('endpoint', 'user_id', 'error_message')
    readonly_fields = ('log_id', 'user_id', 'endpoint', 'method', 'status_code', 
                       'latency_ms', 'timestamp', 'error_message', 'request_size', 'response_size')
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Request Info', {
            'fields': ('log_id', 'endpoint', 'method', 'user_id', 'timestamp')
        }),
        ('Response Info', {
            'fields': ('status_code', 'latency_ms', 'error_message')
        }),
        ('Sizes', {
            'fields': ('request_size', 'response_size'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation; only middleware creates logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Logs are read-only; prevent modifications."""
        return False
