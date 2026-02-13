from pathlib import Path
from agents.base_agent import BaseAgent

BASE_DIR = Path(__file__).resolve().parent.parent

class TaskAgent(BaseAgent):
    def __init__(self, llm_client):
        self.llm = llm_client
        self.prompt = (BASE_DIR / "prompts" / "task_prompt.txt").read_text()

    def evaluate(self, essay: str, question: str) -> dict:
        user_prompt = f"QUESTION:\n{question}\n\nESSAY:\n{essay}"
        response = self.llm.generate(self.prompt, user_prompt)
        return self._parse(response)