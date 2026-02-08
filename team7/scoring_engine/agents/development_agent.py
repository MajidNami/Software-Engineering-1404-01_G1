from pathlib import Path
from agents.base_agent import BaseAgent

BASE_DIR = Path(__file__).resolve().parent.parent

class DevelopmentAgent(BaseAgent):
    def __init__(self, llm_client):
        self.llm = llm_client
        self.prompt = (BASE_DIR / "prompts" / "development_prompt.txt").read_text()

    def evaluate(self, essay: str) -> dict:
        response = self.llm.generate(self.prompt, essay)
        return self._parse(response)