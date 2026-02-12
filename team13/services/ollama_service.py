"""Talks to ollama container to grade student responses."""
import requests
from django.conf import settings


def grade(prompt: str) -> str:
    """Send prompt to Ollama container"""
    base_url = getattr(settings, 'OLLAMA_HOST', 'http://ollama:11434')
    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "model": getattr(settings, 'OLLAMA_MODEL', 'gemma3:4b'),
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.1}
        }
    )
    response.raise_for_status()
    return response.json()['message']['content']
