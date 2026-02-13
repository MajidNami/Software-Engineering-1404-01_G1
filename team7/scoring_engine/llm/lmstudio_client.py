import requests
from llm.base_client import BaseLLMClient


class LMStudioClient(BaseLLMClient):
    """
    Connects to local LM Studio (Gemma, Llama, etc.)
    """

    def __init__(self, base_url="http://localhost:1234/v1", model="gemma-3-12b"):
        self.base_url = base_url
        self.model = model

    def generate(self, system_prompt, user_prompt):
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }

        response = requests.post(url, json=payload)
        return response.json()["choices"][0]["message"]["content"]
