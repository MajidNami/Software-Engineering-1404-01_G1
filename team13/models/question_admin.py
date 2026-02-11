from django.contrib import admin

from team13.models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'text', 'sample_correct_answer', 'question_type', 'created_at', 'modified_at']
    search_fields = ['title', 'question_type']
    readonly_fields = ['created_at', 'modified_at']
