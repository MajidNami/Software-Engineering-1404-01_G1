from django.contrib import admin
from .models import Passage, Question, Option


# =========================
# Inline for Option
# =========================
class OptionInline(admin.TabularInline):
    model = Option
    extra = 4
    min_num = 2
    max_num = 6


# =========================
# Inline for Question
# =========================
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


# =========================
# Question Admin
# =========================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'question_type',
        'passage',
        'score',
    )
    list_filter = (
        'question_type',
        'passage__difficulty_level',
        'passage__topic',
    )
    search_fields = (
        'question_text',
        'passage__title',
    )
    inlines = [OptionInline]


# =========================
# Passage Admin
# =========================
@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'topic',
        'difficulty_level',
        'text_length',
        'version',
        'created_at',
    )
    list_filter = (
        'topic',
        'difficulty_level',
        'rubric_version',
    )
    search_fields = (
        'title',
        'text',
    )
    readonly_fields = ('created_at',)
    inlines = [QuestionInline]


# =========================
# Option Admin (اختیاری)
# =========================
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'question',
        'is_correct',
    )
    list_filter = ('is_correct',)
    search_fields = ('text',)
