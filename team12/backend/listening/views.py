from django.db.models import Count

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import ListeningTest, ListeningSession, ListeningItem, UserAnswer
from .serializers import (
    ListeningTestListSerializer,
    ListeningTestDetailSerializer,
    SessionStartSerializer,
    SessionSerializer,
    SubmitAnswerSerializer,
    EventSerializer,
    ScoreReportSerializer,
    ListeningItemSerializer,
    QuestionSerializer,
)
from .services import ListeningService
from .utils import get_guest_user


def _user(request):
    return request.user if request.user.is_authenticated else get_guest_user()


class TestsListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tests = ListeningTest.objects.filter(is_active=True, is_archived=False)
        serializer = ListeningTestListSerializer(tests, many=True)
        return Response(serializer.data)


class SessionStartView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = SessionStartSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        session = ListeningService.start_session(
            _user(request),
            ser.validated_data['test_id'],
            ser.validated_data['mode'],
        )
        test = session.test
        items = list(test.items.prefetch_related('questions__options').order_by('order'))
        first_item = items[0] if items else None
        first_questions = list(first_item.questions.order_by('order')) if first_item else []
        first_question = first_questions[0] if first_questions else None
        hide_correct = session.mode == 'exam'
        ctx = {'hide_correct': hide_correct}
        item_ser = ListeningItemSerializer(first_item, context=ctx) if first_item else None
        q_ser = QuestionSerializer(first_question, context=ctx) if first_question else None
        all_items_ser = ListeningItemSerializer(items, many=True, context=ctx)
        return Response({
            'session': SessionSerializer(session).data,
            'current_item': item_ser.data if item_ser else None,
            'current_question': q_ser.data if q_ser else None,
            'all_items': all_items_ser.data,
        }, status=status.HTTP_201_CREATED)


class SessionDetailView(APIView):
    permission_classes = [AllowAny]

    def get_session(self, pk):
        return get_object_or_404(ListeningSession, pk=pk, user=_user(self.request))

    def get(self, request, pk):
        session = self.get_session(pk)
        return Response(SessionSerializer(session).data)


class SessionAnswersView(APIView):
    permission_classes = [AllowAny]

    def get_session(self, pk):
        return get_object_or_404(ListeningSession, pk=pk, user=_user(self.request))

    def post(self, request, pk):
        session = self.get_session(pk)
        if session.status != 'active':
            return Response(
                {'detail': 'Session is not active.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = SubmitAnswerSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result = ListeningService.submit_answer(
            session.id,
            ser.validated_data['question_id'],
            ser.validated_data['option_id'],
            ser.validated_data.get('response_time_ms'),
        )
        return Response(result, status=status.HTTP_201_CREATED)


class SessionEventsView(APIView):
    permission_classes = [AllowAny]

    def get_session(self, pk):
        return get_object_or_404(ListeningSession, pk=pk, user=_user(self.request))

    def post(self, request, pk):
        session = self.get_session(pk)
        ser = EventSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ListeningService.log_event(
            session.id,
            ser.validated_data['event_type'],
            ser.validated_data.get('count', 1),
            ser.validated_data.get('extra_data'),
        )
        return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)


class SessionScoreReportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        session = get_object_or_404(ListeningSession, pk=pk, user=_user(request))
        if not hasattr(session, 'score_report'):
            return Response(
                {'detail': 'Score report not available yet.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ScoreReportSerializer(session.score_report).data)


class SessionFinishView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        session = get_object_or_404(ListeningSession, pk=pk, user=_user(request))
        if session.status != 'active':
            return Response(
                {'detail': 'Session already finished.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        report = ListeningService.finish_session(session.id)
        data = dict(ScoreReportSerializer(report).data)
        answers = (
            UserAnswer.objects.filter(session=session)
            .select_related('question', 'selected_option')
            .order_by('question__order')
        )
        total_questions = session.test.items.aggregate(
            total=Count('questions')
        ).get('total') or 0
        answered_count = answers.count()
        correct_count = sum(1 for a in answers if a.is_correct)
        detailed = []
        for i, ua in enumerate(answers, start=1):
            correct_option = ua.question.options.filter(is_correct=True).first()
            detailed.append({
                'id': i,
                'question_text': ua.question.text,
                'correct_answer': correct_option.text if correct_option else '—',
                'your_answer': ua.selected_option.text if ua.selected_option else '—',
            })
        data['answered_count'] = answered_count
        data['correct_count'] = correct_count
        data['total_questions'] = total_questions
        data['detailed_answers'] = detailed
        return Response(data)


class ItemDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, item_id):
        item = get_object_or_404(ListeningItem, pk=item_id)
        return Response(ListeningItemSerializer(item).data)
