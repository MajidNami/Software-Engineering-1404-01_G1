from django.contrib import admin

# Register your models here.

from .models import Lesson, Word

# Registering models to see them in Django Admin
admin.site.register(Lesson)
admin.site.register(Word)