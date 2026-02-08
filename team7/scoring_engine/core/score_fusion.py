"""
Combines analytic scores into final TOEFL band and scaled score.
"""

from core.weights import WEIGHTS

def to_scaled_score(band_score: float) -> int:
    """
    Converts 0–5 band to 0–30 TOEFL writing score.
    """
    safe_band = min(float(band_score), 5.0)
    scaled = (safe_band / 5.0) * 30
    return int(round(scaled))


def compute_holistic_score(analytic_scores: dict) -> float:
    """
    Weighted fusion of analytic scores.

    Args:
        scores (dict): dimension → score (0–5)

    Returns:
        int: Holistic band (0–5)
    """
    if not analytic_scores:
        return 0.0
    
    scores = list(analytic_scores.values())
    avg_score = sum(scores) / len(scores)
    return round(avg_score, 2)