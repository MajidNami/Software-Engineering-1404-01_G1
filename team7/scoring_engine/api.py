import os
from .llm.openai_client import OpenAIClient
from .pipeline.scorer import TOEFLScorer


def score_essay(essay: str, question: str) -> float:
    """
    Returns only the TOEFL scaled score (0–5)
    """
    #api_key="g4a--DDlhVlIhrRWPgBmbu0eFwk2Skvb5-RjaQMv-ZJQOP8",
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    client = OpenAIClient(
        api_key=api_key,
        model="gpt-4o-mini",
        base_url="https://api.gpt4-all.xyz/v1"
    )

    scorer = TOEFLScorer(client)

    result = scorer.score(
        essay=essay,
        question=question
    )

    return result["band_score"]
