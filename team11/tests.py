from pathlib import Path
import json
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from .models import Submission, WritingSubmission, AssessmentResult, SubmissionType, AnalysisStatus
from .services import assess_writing, assess_speaking
from .services.ai_service import API_BASE_URL, API_KEY, DEEPSEEK_MODEL


class Team11AISmokeTests(TestCase):
    def setUp(self):
        # Quick availability check for provider 
        try:
            client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY, timeout=300.0)
            print("[Provider Check] Sending minimal chat request...")
            client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
                temperature=0.0,
            )
            print("[Provider Check] OK")
        except (APIConnectionError, RateLimitError, APIError) as e:
            print(f"[Provider Check] FAILED: {e}")
            self.skipTest(f"Provider unavailable: {e}")
        except Exception as e:
            print(f"[Provider Check] FAILED (unexpected): {e}")
            self.skipTest(f"Provider check failed: {e}")

    def _skip_if_external_failure(self, result, context):
        error = (result or {}).get("error") or ""
        error_lower = error.lower()

        if any(term in error_lower for term in [
            "failed to connect",
            "timeout",
            "rate limit",
            "api connection",
            "transcription service error",
        ]):
            print(f"[{context}] External service failure: {error}")
            self.skipTest(f"{context} skipped due to external service error: {error}")

        if "invalid file format" in error_lower:
            print(f"[{context}] Invalid audio format: {error}")
            self.skipTest(f"{context} skipped due to invalid audio format: {error}")

    def test_speaking_assessment(self):
        topic = "Do you prefer to live in a big city or a small town? Explain your opinion using specific reasons and examples."
        project_root = Path(__file__).resolve().parents[1]
        audio_path = project_root / "team11" / "static" / "team11" / "public" / "audio" / "sample_answer.mp3"
        print(f"Testing speaking assessment with audio file: {audio_path}")
        if not audio_path.exists():
            self.skipTest(f"Audio file not found: {audio_path}")

        result = assess_speaking(topic, str(audio_path), duration_seconds=30)

        print("Speaking assessment success:", result.get("success"))
        print("Speaking overall_score:", result.get("overall_score"))
        print("Speaking transcription:", result.get("transcription"))
        if result.get("error"):
            print("Speaking error:", result.get("error"))

        if not result.get("success"):
            self._skip_if_external_failure(result, "Speaking assessment")

        self.assertTrue(result.get("success"), msg=result.get("error"))
        self.assertIsNotNone(result.get("overall_score"))
        self.assertTrue(result.get("transcription"))
        
    def test_writing_assessment(self):
        topic = "Do you prefer to live in a big city or a small town? Explain your opinion using specific reasons and examples."
        text_body = (
            "I prefer to live in a small town because life is calmer and more personal. "
            "In a small town, people know each other, which creates a strong sense of community. "
            "For example, neighbors often help each other and local events feel more welcoming. "
            "Also, daily life is less stressful because traffic is lighter and everything is closer. "
            "Although big cities offer more entertainment, I value peace and close relationships more."
        )
        word_count = len(text_body.split())

        result = assess_writing(topic, text_body, word_count)

        print("Writing assessment success:", result.get("success"))
        print("Writing overall_score:", result.get("overall_score"))
        print("Writing feedback:", result.get("feedback_summary"))
        if result.get("error"):
            print("Writing error:", result.get("error"))

        if not result.get("success"):
            self._skip_if_external_failure(result, "Writing assessment")

        self.assertTrue(result.get("success"), msg=result.get("error"))
        self.assertIsNotNone(result.get("overall_score"))


class Team11AuthTests(TestCase):
    def test_ping_requires_auth(self):
        response = self.client.get("/team11/ping/")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json().get("detail"), "Authentication required")

    def test_ping_with_auth(self):
        user = get_user_model().objects.create_user(
            email="test_user@example.com",
            password="testpass123",
        )
        self.client.force_login(user)

        response = self.client.get("/team11/ping/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body.get("team"), "team11")
        self.assertTrue(body.get("ok"))


class Team11SubmissionApiTests(TestCase):
    databases = {"default", "team11"}

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="submit_user@example.com",
            password="testpass123",
        )
        self.client.force_login(self.user)

    def test_submit_writing_rejects_empty_text(self):
        response = self.client.post(
            "/team11/api/submit-writing/",
            data=json.dumps(
                {
                    "topic": "Sample topic",
                    "text_body": "",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("error"),
            "متن ارسالی نمی‌تواند خالی باشد.",
        )
        self.assertEqual(Submission.objects.using("team11").count(), 0)

    @patch("team11.views.threading.Thread")
    def test_submit_writing_creates_submission_and_returns_202(self, thread_mock):
        response = self.client.post(
            "/team11/api/submit-writing/",
            data=json.dumps(
                {
                    "topic": "Test topic",
                    "text_body": "This is a valid writing submission body.",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 202)
        body = response.json()
        self.assertTrue(body.get("success"))
        self.assertEqual(body.get("status"), "processing")

        submission = Submission.objects.using("team11").get(submission_id=body["submission_id"])
        self.assertEqual(submission.user_id, self.user.id)
        self.assertEqual(submission.submission_type, SubmissionType.WRITING)
        self.assertEqual(submission.status, AnalysisStatus.IN_PROGRESS)
        self.assertTrue(
            WritingSubmission.objects.using("team11").filter(submission=submission).exists()
        )
        thread_mock.assert_called_once()
        thread_mock.return_value.start.assert_called_once()

    def test_submit_writing_rejects_persian_text(self):
        response = self.client.post(
            "/team11/api/submit-writing/",
            data=json.dumps(
                {
                    "topic": "Test topic",
                    "text_body": "این یک متن فارسی است.",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "فقط متن انگلیسی قابل قبول است.")
        self.assertEqual(Submission.objects.using("team11").count(), 0)

    def test_submission_status_returns_failed_message_from_assessment_result(self):
        submission = Submission.objects.using("team11").create(
            user_id=self.user.id,
            submission_type=SubmissionType.WRITING,
            status=AnalysisStatus.FAILED,
        )
        AssessmentResult.objects.using("team11").create(
            submission=submission,
            feedback_summary="Custom failure from assessment",
            suggestions=[],
        )

        response = self.client.get(f"/team11/api/submission-status/{submission.submission_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "failed")
        self.assertEqual(
            response.json().get("message"),
            "Custom failure from assessment",
        )
