from django.contrib import admin
from .models import Question, Evaluation, DetailedScore

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'task_type', 'mode', 'difficulty')

class DetailedScoreInline(admin.TabularInline):
    model = DetailedScore
    extra = 0

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('evaluation_id', 'user_id', 'overall_score', 'created_at')
    inlines = [DetailedScoreInline]