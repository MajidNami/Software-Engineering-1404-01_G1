from django.contrib import admin

from team13.models import Prompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['name', 'prompt_text', 'created_at', 'modified_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'modified_at']
