"""This is a singleton internal service which transcripts audio to text.
We use singleton architecture so that we load the model once and use it multiple times.
We use openai-whisper package for this.

⚠️ IMPORTANT:
This image build should be with VPN because we are banned.
The model will be cached in the Docker image during build and no network is needed at runtime.
"""
import django.conf.settings
import threading
import whisper


class WhisperTranscriber:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> 'WhisperTranscriber':
        """Create singleton instance if it doesn't exist"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        print("Initializing Whisper transcription service...")
        self.model = whisper.load_model(getattr(django.conf.settings, "WHISPER_MODEL_SIZE", "base"))
        self.is_ready = True
        print("Whisper service ready!")

    def transcribe(self, audio: bytes) -> dict:
        """Main transcription method for other services to use"""
        result = self.model.transcribe(audio)
        return {
            'text': result['text'],
            'language': result.get('language', 'en'),
        }


whisper_transcriber = WhisperTranscriber()
