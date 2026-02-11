"""This is a singleton internal service which runs LLM for exam grading.
We use singleton architecture so that we load the model once and use it multiple times.
We use ollama package for this.

⚠️ IMPORTANT:
This image build should be with VPN because we are banned.
The model will be cached in the Docker image during build and no network is needed at runtime.
"""
import django.conf.settings
import threading
import ollama
import subprocess
import time


class OllamaLLM:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> 'OllamaLLM':
        """Create singleton instance if it doesn't exist"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        print("Initializing Ollama grading service...")
        # Start Ollama server
        self.process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(4)  # Wait for server to start
        # Load model from settings
        self.model_name = getattr(django.conf.settings, "OLLAMA_MODEL", "gemma3:4b")
        # Warm up model (load into memory)
        ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": "warmup"}]
        )
        self.is_ready = True
        print(f"Ollama service ready with model: {self.model_name}!")

    def get_response(self, prompt: str) -> str:
        """Main method for using llm for other services to use"""
        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            options={'temperature': 0.1}
        )
        return response['message']['content']


ollama_llm = OllamaLLM()
