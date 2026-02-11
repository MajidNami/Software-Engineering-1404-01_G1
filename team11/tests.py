from pathlib import Path

from django.test import TestCase
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

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
