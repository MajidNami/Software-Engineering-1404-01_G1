import re

class BaseAgent:
    def _parse(self, text: str) -> dict:
        text = text.strip()
        lines = text.split("\n")
        
        score_match = re.search(r'\d+', lines[0])
        
        if score_match:
            raw_score = int(score_match.group())
            if raw_score > 5:
                score = 5 
            else:
                score = raw_score
        else:
            score = 0
            
        explanation = "\n".join(lines[1:]).replace("EXPLANATION:", "").strip()
        
        return {"score": int(score), "explanation": explanation}