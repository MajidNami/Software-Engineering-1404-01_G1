def calculate_score(correct_count, total_questions):
    """
    Convert raw score to TOEFL-scaled score (0-30).
    Uses linear scaling: (correct / total) * 30, rounded to nearest integer.
    """
    if total_questions == 0:
        return 0
    raw_ratio = correct_count / total_questions
    scaled = round(raw_ratio * 30)
    return max(0, min(30, scaled))


def calculate_accuracy(correct_count, total_questions):
    """Return accuracy as a percentage (0-100)."""
    if total_questions == 0:
        return 0.0
    return round((correct_count / total_questions) * 100, 1)
