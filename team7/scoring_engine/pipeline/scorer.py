from agents.task_agent import TaskAgent
from agents.organization_agent import OrganizationAgent
from agents.development_agent import DevelopmentAgent
from agents.language_agent import LanguageAgent
from core.score_fusion import compute_holistic_score, to_scaled_score
import time

class TOEFLScorer:
    def __init__(self, llm_client):
        self.task_agent = TaskAgent(llm_client)
        self.org_agent = OrganizationAgent(llm_client)
        self.dev_agent = DevelopmentAgent(llm_client)
        self.lang_agent = LanguageAgent(llm_client)

    def score(self, essay, question):
        results = {}
        
        results["task"] = self.task_agent.evaluate(essay, question)
        time.sleep(1)
        results["organization"] = self.org_agent.evaluate(essay)
        time.sleep(1)
        results["development"] = self.dev_agent.evaluate(essay)
        time.sleep(1)
        results["language"] = self.lang_agent.evaluate(essay)

        analytic_scores = {k: v["score"] for k, v in results.items()}

        band = compute_holistic_score(analytic_scores) 
        scaled = to_scaled_score(band)            

        return {
            "analytic": results,
            "band_score": round(band, 1),
            "scaled_score": int(scaled) 
        }