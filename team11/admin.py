from django.contrib import admin
from .models import (
    Submission, WritingSubmission, ListeningSubmission, 
    AssessmentResult, QuestionCategory, Question
)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['submission_id', 'user_id', 'submission_type', 'overall_score', 'status', 'created_at']
    list_filter = ['submission_type', 'status', 'created_at']
    search_fields = ['submission_id', 'user_id']
    readonly_fields = ['submission_id', 'created_at']
    ordering = ['-created_at']


@admin.register(WritingSubmission)
class WritingSubmissionAdmin(admin.ModelAdmin):
    list_display = ['submission', 'topic', 'word_count']
    search_fields = ['topic', 'text_body']
    readonly_fields = ['submission']


@admin.register(ListeningSubmission)
class ListeningSubmissionAdmin(admin.ModelAdmin):
    list_display = ['submission', 'topic', 'duration_seconds']
    search_fields = ['topic']
    readonly_fields = ['submission']


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['result_id', 'submission', 'created_at']
    readonly_fields = ['result_id', 'created_at']
    search_fields = ['submission__submission_id']


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'question_type', 'is_active']
    list_filter = ['question_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['category_id']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'category', 'difficulty_level', 'is_active']
    list_filter = ['category', 'difficulty_level', 'is_active']
    search_fields = ['question_text']
    readonly_fields = ['question_id']
    
    def question_text_short(self, obj):
        return obj.question_text[:80] + '...' if len(obj.question_text) > 80 else obj.question_text
    question_text_short.short_description = 'Question'
