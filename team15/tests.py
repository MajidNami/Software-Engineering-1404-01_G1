from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Test, Passage, Question, TestAttempt, Answer
from .scoring import calculate_score, calculate_accuracy


TEST_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "team15": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}


class ScoringTests(TestCase):
    def test_perfect_score(self):
        self.assertEqual(calculate_score(10, 10), 30)

    def test_zero_score(self):
        self.assertEqual(calculate_score(0, 10), 0)

    def test_half_score(self):
        self.assertEqual(calculate_score(5, 10), 15)

    def test_no_questions(self):
        self.assertEqual(calculate_score(0, 0), 0)

    def test_accuracy_perfect(self):
        self.assertEqual(calculate_accuracy(10, 10), 100.0)

    def test_accuracy_zero(self):
        self.assertEqual(calculate_accuracy(0, 10), 0.0)

    def test_accuracy_no_questions(self):
        self.assertEqual(calculate_accuracy(0, 0), 0.0)


@override_settings(DATABASES=TEST_DATABASES)
class ModelTests(TestCase):
    databases = {"default", "team15"}

    def setUp(self):
        self.test_obj = Test.objects.create(
            title="Sample TOEFL Reading", mode="exam", time_limit=60
        )
        self.passage = Passage.objects.create(
            test=self.test_obj, title="Passage 1",
            content="This is a sample passage.", order=1
        )
        self.question = Question.objects.create(
            passage=self.passage,
            question_text="What is the main idea?",
            choices=["A) Idea 1", "B) Idea 2", "C) Idea 3", "D) Idea 4"],
            correct_answer="A) Idea 1",
            order=1,
        )

    def test_soft_delete(self):
        self.test_obj.soft_delete()
        self.assertEqual(Test.objects.count(), 0)
        self.assertEqual(Test.all_objects.count(), 1)

    def test_question_str(self):
        self.assertIn("Q1:", str(self.question))

    def test_passage_ordering(self):
        p2 = Passage.objects.create(
            test=self.test_obj, title="Passage 2", content="...", order=0
        )
        passages = list(Passage.objects.filter(test=self.test_obj))
        self.assertEqual(passages[0].id, p2.id)


@override_settings(DATABASES=TEST_DATABASES)
class APITests(TestCase):
    databases = {"default", "team15"}

    def setUp(self):
        self.client = APIClient()
        self.user_id = "test-user-123"
        self.test_obj = Test.objects.create(
            title="API Test", mode="practice", time_limit=0
        )
        self.passage = Passage.objects.create(
            test=self.test_obj, title="P1", content="Content here.", order=1
        )
        self.q1 = Question.objects.create(
            passage=self.passage,
            question_text="Q1?",
            choices=["A", "B", "C", "D"],
            correct_answer="A",
            order=1,
        )
        self.q2 = Question.objects.create(
            passage=self.passage,
            question_text="Q2?",
            choices=["A", "B", "C", "D"],
            correct_answer="B",
            order=2,
        )

    def test_list_tests(self):
        res = self.client.get("/team15/api/tests/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "API Test")

    def test_list_tests_filter_mode(self):
        Test.objects.create(title="Exam Test", mode="exam")
        res = self.client.get("/team15/api/tests/?mode=exam")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "Exam Test")

    def test_detail(self):
        res = self.client.get(f"/team15/api/tests/{self.test_obj.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "API Test")
        self.assertEqual(len(res.data["passages"]), 1)
        self.assertEqual(len(res.data["passages"][0]["questions"]), 2)

    def test_detail_not_found(self):
        res = self.client.get("/team15/api/tests/9999/")
        self.assertEqual(res.status_code, 404)

    def test_start_attempt(self):
        res = self.client.post("/team15/api/attempts/start/", {
            "test_id": self.test_obj.id,
            "user_id": self.user_id,
        }, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertIn("attempt_id", res.data)

    def test_start_attempt_requires_user_id(self):
        res = self.client.post("/team15/api/attempts/start/", {
            "test_id": self.test_obj.id,
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_start_attempt_resumes(self):
        res1 = self.client.post("/team15/api/attempts/start/", {
            "test_id": self.test_obj.id,
            "user_id": self.user_id,
        }, format="json")
        res2 = self.client.post("/team15/api/attempts/start/", {
            "test_id": self.test_obj.id,
            "user_id": self.user_id,
        }, format="json")
        self.assertEqual(res1.data["attempt_id"], res2.data["attempt_id"])

    def test_practice_flow(self):
        # Start
        res = self.client.post("/team15/api/attempts/start/", {
            "test_id": self.test_obj.id,
            "user_id": self.user_id,
        }, format="json")
        attempt_id = res.data["attempt_id"]

        # Answer Q1 correctly
        res = self.client.post("/team15/api/attempts/answer/", {
            "attempt_id": attempt_id,
            "question_id": self.q1.id,
            "selected_answer": "A",
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["is_correct"])

        # Answer Q2 incorrectly
        res = self.client.post("/team15/api/attempts/answer/", {
            "attempt_id": attempt_id,
            "question_id": self.q2.id,
            "selected_answer": "C",
        }, format="json")
        self.assertFalse(res.data["is_correct"])
        self.assertEqual(res.data["correct_answer"], "B")

        # Finish practice
        res = self.client.post("/team15/api/attempts/finish/", {
            "attempt_id": attempt_id,
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "completed")
        self.assertEqual(res.data["correct"], 1)
        self.assertEqual(res.data["total"], 2)
        self.assertEqual(res.data["score"], 15)

    def test_exam_flow(self):
        exam = Test.objects.create(title="Exam", mode="exam", time_limit=20)
        p = Passage.objects.create(test=exam, title="EP", content="...", order=1)
        eq1 = Question.objects.create(
            passage=p, question_text="EQ1?",
            choices=["A", "B", "C", "D"], correct_answer="A", order=1
        )
        eq2 = Question.objects.create(
            passage=p, question_text="EQ2?",
            choices=["A", "B", "C", "D"], correct_answer="B", order=2
        )

        # Start
        res = self.client.post("/team15/api/attempts/start/", {
            "test_id": exam.id,
            "user_id": self.user_id,
        }, format="json")
        attempt_id = res.data["attempt_id"]

        # Bulk submit
        res = self.client.post("/team15/api/attempts/submit/", {
            "attempt_id": attempt_id,
            "answers": [
                {"question_id": eq1.id, "selected_answer": "A"},
                {"question_id": eq2.id, "selected_answer": "B"},
            ],
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["score"], 30)
        self.assertEqual(res.data["correct"], 2)
        self.assertEqual(res.data["status"], "completed")

    def test_attempt_result(self):
        res = self.client.post("/team15/api/attempts/start/", {
            "test_id": self.test_obj.id,
            "user_id": self.user_id,
        }, format="json")
        attempt_id = res.data["attempt_id"]
        self.client.post("/team15/api/attempts/answer/", {
            "attempt_id": attempt_id,
            "question_id": self.q1.id,
            "selected_answer": "A",
        }, format="json")
        self.client.post("/team15/api/attempts/finish/", {
            "attempt_id": attempt_id,
        }, format="json")

        res = self.client.get(f"/team15/api/attempts/{attempt_id}/result/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("answers", res.data)
        self.assertEqual(res.data["correct"], 1)

    def test_user_history(self):
        res = self.client.get(f"/team15/api/history/?user_id={self.user_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_user_history_missing_param(self):
        res = self.client.get("/team15/api/history/")
        self.assertEqual(res.status_code, 400)

    def test_user_dashboard(self):
        res = self.client.get(f"/team15/api/dashboard/?user_id={self.user_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["total_attempts"], 0)

    def test_user_dashboard_missing_param(self):
        res = self.client.get("/team15/api/dashboard/")
        self.assertEqual(res.status_code, 400)

    def test_ping(self):
        res = self.client.get("/team15/ping/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["team"], "team15")
