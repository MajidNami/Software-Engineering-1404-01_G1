from django.contrib import admin

from team13.models import prompt


@admin.register(prompt.Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'prompt_text', 'created', 'modified']
    search_fields = ['name']
    readonly_fields = ['created', 'modified']
