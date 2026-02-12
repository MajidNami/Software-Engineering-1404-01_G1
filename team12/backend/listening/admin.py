from django.contrib import admin
from .models import (
    ListeningTest,
    ListeningItem,
    Question,
    ChoiceOption,
    ListeningSession,
    UserAnswer,
    AntiCheatEvent,
    ScoreReport,
)


class ListeningItemInline(admin.StackedInline):
    model = ListeningItem
    extra = 0
    ordering = ['order']


@admin.register(ListeningTest)
class ListeningTestAdmin(admin.ModelAdmin):
    list_display = ['title', 'version_id', 'total_items', 'is_active', 'is_archived', 'created_at']
    list_filter = ['is_active', 'is_archived']
    inlines = [ListeningItemInline]


class ChoiceOptionInline(admin.TabularInline):
    model = ChoiceOption
    extra = 0
    ordering = ['order']


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    ordering = ['order']
    show_change_link = True


@admin.register(ListeningItem)
class ListeningItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'test', 'item_type', 'difficulty', 'order', 'has_thumbnail']
    list_filter = ['item_type', 'difficulty']
    inlines = [QuestionInline]

    def has_thumbnail(self, obj):
        return bool(obj.thumbnail_source)
    has_thumbnail.boolean = True
    has_thumbnail.short_description = 'Thumbnail'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'question_type', 'order']
    list_filter = ['question_type']
    inlines = [ChoiceOptionInline]


@admin.register(ListeningSession)
class ListeningSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'test', 'mode', 'status', 'start_time', 'end_time']
    list_filter = ['mode', 'status']


@admin.register(ScoreReport)
class ScoreReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'total_score', 'main_idea', 'detail', 'inference', 'organization', 'pragmatic']
