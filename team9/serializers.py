from rest_framework import serializers
from .models import Lesson, Word

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        # Including all fields to be sent to the frontend
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    # This will nest the words inside the lesson data
    words = WordSerializer(many=True, read_only=True)
    # Granular progress based on ticks (read-only calculated field)
    progress_percent = serializers.ReadOnlyField()

    class Meta:
        model = Lesson
        fields = ['id', 'user_id', 'title', 'description', 'created_at', 'words', 'progress_percent']