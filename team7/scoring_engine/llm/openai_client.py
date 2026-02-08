import time
from openai import OpenAI
from llm.base_client import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model="gpt-4o-mini", base_url="https://api.gpt4-all.xyz/v1"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate(self, system_prompt, user_prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    timeout=60.0
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                else:
                    return "Score: 0\nError: Maximum retries reached due to connection issues."