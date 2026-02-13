from rest_framework import serializers
from .models import Test, Passage, Question, TestAttempt, Answer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "question_text", "question_type", "choices", "order"]


class QuestionWithAnswerSerializer(serializers.ModelSerializer):
    """Includes correct_answer — used in results."""
    class Meta:
        model = Question
        fields = ["id", "question_text", "question_type", "choices", "correct_answer", "order"]


class PassageSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Passage
        fields = ["id", "title", "content", "order", "questions"]


class PassageWithAnswersSerializer(serializers.ModelSerializer):
    questions = QuestionWithAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Passage
        fields = ["id", "title", "content", "order", "questions"]


class TestListSerializer(serializers.ModelSerializer):
    passage_count = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ["id", "title", "mode", "time_limit", "is_active", "passage_count", "question_count", "created_at"]

    def get_passage_count(self, obj):
        return obj.passages.count()

    def get_question_count(self, obj):
        total = 0
        for p in obj.passages.all():
            total += p.questions.count()
        return total


class TestDetailSerializer(serializers.ModelSerializer):
    passages = PassageSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ["id", "title", "mode", "time_limit", "is_active", "passages", "created_at"]


class StartAttemptSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    user_id = serializers.CharField(max_length=36, required=False)


class SubmitAnswerSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    selected_answer = serializers.CharField(max_length=255)
    time_spent = serializers.IntegerField(required=False, default=None)


class BulkAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_answer = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    time_spent = serializers.IntegerField(required=False, allow_null=True, default=None)


class SubmitExamSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    answers = BulkAnswerItemSerializer(many=True)


class FinishPracticeSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()


class AnswerResultSerializer(serializers.ModelSerializer):
    question = QuestionWithAnswerSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "question", "selected_answer", "is_correct", "time_spent", "answered_at"]


class AttemptResultSerializer(serializers.ModelSerializer):
    answers = AnswerResultSerializer(many=True, read_only=True)
    test_title = serializers.CharField(source="test.title", read_only=True)
    test_mode = serializers.CharField(source="test.mode", read_only=True)

    class Meta:
        model = TestAttempt
        fields = ["id", "test_title", "test_mode", "status", "score", "total_time",
                  "started_at", "finished_at", "answers"]


class AttemptHistorySerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source="test.title", read_only=True)
    test_mode = serializers.CharField(source="test.mode", read_only=True)

    class Meta:
        model = TestAttempt
        fields = ["id", "test_title", "test_mode", "status", "score", "total_time",
                  "started_at", "finished_at"]
