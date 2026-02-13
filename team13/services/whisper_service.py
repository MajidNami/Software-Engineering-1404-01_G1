"""Talks to whisper container to transcribe audio to text."""
import requests
from django.conf import settings


def transcribe(audio_file) -> dict:
    """Send audio file to whisper container"""
    base_url = getattr(settings, 'WHISPER_HOST', 'http://team13-whisper-1:9000')
    files = {'audio_file': (audio_file.name, audio_file.read(), audio_file.content_type)}
    response = requests.post(
        f"{base_url}/asr",
        params={
            "task": "transcribe",
            "language": "en",
            "output": "json"
        },
        files=files
    )
    response.raise_for_status()
    result = response.json()
    return {
        'text': result.get('text', ''),
        'language': result.get('language', 'en'),
    }
