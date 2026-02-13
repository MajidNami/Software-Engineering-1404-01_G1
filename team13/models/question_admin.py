from django.contrib import admin

from team13.models import question


@admin.register(question.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'text', 'sample_correct_answer', 'question_type', 'created', 'modified']
    search_fields = ['title', 'question_type']
    readonly_fields = ['created', 'modified']
