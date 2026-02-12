from django.db import transaction
from django.utils import timezone
from .models import (
    ListeningTest,
    ListeningSession,
    UserAnswer,
    AntiCheatEvent,
    ScoreReport,
    Question,
    ChoiceOption,
)


class ListeningService:
    @staticmethod
    def start_session(user, test_id: int, mode: str) -> ListeningSession:
        test = ListeningTest.objects.get(pk=test_id, is_active=True)
        with transaction.atomic():
            session = ListeningSession.objects.create(user=user, test=test, mode=mode)
        return session

    @staticmethod
    def submit_answer(session_id: int, question_id: int, option_id: int, response_time_ms: int = None):
        session = ListeningSession.objects.get(pk=session_id, status='active')
        question = Question.objects.get(pk=question_id)
        option = ChoiceOption.objects.get(pk=option_id, question=question)
        is_correct = option.is_correct
        UserAnswer.objects.update_or_create(
            session=session,
            question=question,
            defaults={
                'selected_option': option,
                'is_correct': is_correct,
                'response_time_ms': response_time_ms,
            },
        )
        correct_option = question.options.filter(is_correct=True).first()
        explanation = question.explanation if session.mode == 'practice' else ''
        return {
            'is_correct': is_correct,
            'correct_option_id': correct_option.id if correct_option else None,
            'explanation': explanation,
        }

    @staticmethod
    def finish_session(session_id: int) -> ScoreReport:
        session = ListeningSession.objects.get(pk=session_id, status='active')
        with transaction.atomic():
            session.status = 'finished'
            session.end_time = timezone.now()
            session.save()
            report = ScoringEngine.calculate(session)
        return report

    @staticmethod
    def log_event(session_id: int, event_type: str, count: int = 1, extra_data: dict = None):
        session = ListeningSession.objects.get(pk=session_id)
        AntiCheatEvent.objects.create(
            session=session,
            event_type=event_type,
            count=count,
            extra_data=extra_data or {},
        )


class ScoringEngine:
    MAX_SCORE = 30

    @staticmethod
    def calculate(session: ListeningSession) -> ScoreReport:
        answers = UserAnswer.objects.filter(session=session).select_related(
            'question', 'selected_option'
        )
        total_questions = answers.count()
        if total_questions == 0:
            raw = 0
            subscores = {}
        else:
            correct = sum(1 for a in answers if a.is_correct)
            by_type = {}
            for a in answers:
                qt = a.question.question_type
                if qt not in by_type:
                    by_type[qt] = {'correct': 0, 'total': 0}
                by_type[qt]['total'] += 1
                if a.is_correct:
                    by_type[qt]['correct'] += 1
            raw = (correct / total_questions) * 100 if total_questions else 0
            subscores = {
                k: int((v['correct'] / v['total']) * 10) if v['total'] else 0
                for k, v in by_type.items()
            }
        total_score = min(30, int((raw / 100) * 30))
        report, _ = ScoreReport.objects.update_or_create(
            session=session,
            defaults={
                'total_score': total_score,
                'main_idea': subscores.get('main_idea', 0),
                'detail': subscores.get('detail', 0),
                'inference': subscores.get('inference', 0),
                'organization': subscores.get('organization', 0),
                'pragmatic': subscores.get('pragmatic', 0),
            },
        )
        return report
