from django.contrib import admin
from .models import Test, Passage, Question, TestAttempt, Answer


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "mode", "time_limit", "is_active", "created_at"]
    list_filter = ["mode", "is_active"]
    search_fields = ["title"]


@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "test", "order", "created_at"]
    list_filter = ["test"]
    search_fields = ["title", "content"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "question_text_short", "passage", "question_type", "correct_answer", "order"]
    list_filter = ["question_type", "passage__test"]
    search_fields = ["question_text"]

    def question_text_short(self, obj):
        return obj.question_text[:80]
    question_text_short.short_description = "Question"


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "test", "user_id", "status", "score", "started_at", "finished_at"]
    list_filter = ["status", "test"]
    search_fields = ["user_id"]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["id", "attempt", "question", "selected_answer", "is_correct", "answered_at"]
    list_filter = ["is_correct"]
    search_fields = ["selected_answer"]
