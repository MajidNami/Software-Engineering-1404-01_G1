from rest_framework import serializers
from .models import (
    ListeningTest,
    ListeningItem,
    Question,
    ChoiceOption,
    ListeningSession,
    UserAnswer,
    ScoreReport,
    AntiCheatEvent,
)


class ChoiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceOption
        fields = ['id', 'label', 'text', 'is_correct']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('hide_correct'):
            data.pop('is_correct', None)
        return data


class QuestionSerializer(serializers.ModelSerializer):
    options = ChoiceOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'score_weight', 'order', 'options', 'explanation']


class ListeningItemSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    audio_source = serializers.ReadOnlyField()
    thumbnail_source = serializers.ReadOnlyField()

    class Meta:
        model = ListeningItem
        fields = [
            'id', 'audio', 'audio_url', 'audio_source',
            'thumbnail', 'thumbnail_url', 'thumbnail_source',
            'difficulty', 'topic_tag', 'transcript', 'item_type', 'order', 'questions',
        ]


class ListeningTestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningTest
        fields = ['id', 'title', 'version_id', 'total_items', 'is_active']


class ListeningTestDetailSerializer(serializers.ModelSerializer):
    items = ListeningItemSerializer(many=True, read_only=True)

    class Meta:
        model = ListeningTest
        fields = ['id', 'title', 'version_id', 'total_items', 'items']


class SessionStartSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    mode = serializers.ChoiceField(choices=[('practice', 'Practice'), ('exam', 'Exam')])


class SessionSerializer(serializers.ModelSerializer):
    test = ListeningTestListSerializer(read_only=True)

    class Meta:
        model = ListeningSession
        fields = ['id', 'test', 'mode', 'status', 'start_time', 'end_time']


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField()
    response_time_ms = serializers.IntegerField(required=False, allow_null=True)


class EventSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=[('focus_loss', 'Focus Loss'), ('replay', 'Replay')])
    count = serializers.IntegerField(default=1, min_value=1)
    extra_data = serializers.JSONField(required=False, default=dict)


class ScoreReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreReport
        fields = [
            'id', 'session', 'total_score', 'main_idea', 'detail',
            'inference', 'organization', 'pragmatic', 'created_at',
        ]
