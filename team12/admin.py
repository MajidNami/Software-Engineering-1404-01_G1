from django.contrib import admin

from .models import (
    ListeningEventLog,
    ListeningPracticeAnswer,
    ListeningPracticeSession,
)


admin.site.register(ListeningPracticeSession)
admin.site.register(ListeningPracticeAnswer)
admin.site.register(ListeningEventLog)
