from django.db import models

from team13.models import base_models
from team13.models import question


class Prompt(base_models.TimeModel):
    """A configurable prompt template for generating AI evaluation requests for student responses. These prompts are
    dynamically constructed to assess student work against standardized  scoring rubrics (ETS-based). The system
    automatically appends the question context, expected answer, and student's actual response to the base prompt text.
    """
    name = models.CharField(max_length=100)
    prompt_text = models.TextField()
    is_active = models.BooleanField(default=False)

    def get_prompt(self, _question: question.Question, student_response: str):
        base_prompt = f"{self.prompt_text}\n\n"
        if _question.question_type == question.Question.WRITING_QUESTION_TYPE:
            return base_prompt + self._get_writing_prompt(_question, student_response)
        elif _question.question_type == question.Question.SPEAKING_QUESTION_TYPE:
            return base_prompt + self._get_speaking_prompt(_question, student_response)

    def _get_writing_prompt(self, _question: question.Question, student_response: str):
        return (f"Writing Task: {_question.title}\n"
                f"Question: {_question.text}\n\n"
                f"Student's Response: {student_response}\n\n"
                f"Evaluate this writing response using ETS scoring criteria:\n\n"
                f"SCORE (0-4):\n"
                f"4 - Demonstrates clear and consistent mastery\n"
                f"3 - Demonstrates reasonable mastery\n"
                f"2 - Demonstrates developing mastery\n"
                f"1 - Demonstrates inconsistent mastery\n"
                f"0 - Demonstrates very little or no mastery\n\n"
                f"RUBRIC CATEGORIES (Rate each 0-4):\n"
                f"• Task Achievement: Addresses the prompt completely\n"
                f"• Coherence & Organization: Logical flow and structure\n"
                f"• Vocabulary: Range and precision of word choice\n"
                f"• Grammar: Sentence structure and accuracy\n"
                f"• Mechanics: Spelling, punctuation, capitalization\n\n"
                f"DETAILED FEEDBACK:\n"
                f"Strengths:\n"
                f"- [List 2-3 specific strengths]\n\n"
                f"Areas for Improvement:\n"
                f"- [List 2-3 specific areas with suggestions]\n\n"
                f"Sample strong response for reference:\n"
                f"{_question.sample_correct_answer}\n\n"
                f"---\n"
                f"You MUST return ONLY a valid JSON object with this exact structure:\n"
                f"{{\n"
                f'  "score": <integer 0-4>,\n'
                f'  "category_scores": {{\n'
                f'    "task_achievement": <integer 0-4>,\n'
                f'    "coherence": <integer 0-4>,\n'
                f'    "vocabulary": <integer 0-4>,\n'
                f'    "grammar": <integer 0-4>,\n'
                f'    "mechanics": <integer 0-4>\n'
                f'  }},\n'
                f'  "feedback": {{\n'
                f'    "summary": "<2-3 sentences overall assessment>",\n'
                f'    "strengths": ["<strength1>", "<strength2>", "<strength3>"],\n'
                f'    "improvements": ["<improvement1>", "<improvement2>", "<improvement3>"],\n'
                f'    "suggestions": "<specific advice for improvement>"\n'
                f'  }}\n'
                f"}}\n"
                f"Do NOT include any other text, explanation, or markdown formatting. Only the JSON object.")

    def _get_speaking_prompt(self, _question: question.Question, student_response: str):
        return (f"Speaking Task: {_question.title}\n"
                f"Question: {_question.text}\n\n"
                f"Student's Response: {student_response}\n\n"
                f"Evaluate this speaking response using ETS TOEFL Speaking Rubric:\n\n"
                f"SCORE (0-4):\n"
                f"4 - High: Responds well to task, clear & coherent\n"
                f"3 - Good: Addresses task, generally understandable\n"
                f"2 - Fair: Limited in completeness or clarity\n"
                f"1 - Poor: Little or no meaningful response\n"
                f"0 - No response\n\n"
                f"RUBRIC CATEGORIES (Rate each 0-4):\n"
                f"• Delivery: Flow, pace, pronunciation, intonation\n"
                f"• Language Use: Grammar, vocabulary, complexity\n"
                f"• Topic Development: Content, reasoning, examples\n\n"
                f"DETAILED FEEDBACK:\n"
                f"Strengths:\n"
                f"- [List specific speaking strengths]\n\n"
                f"Areas for Improvement:\n"
                f"- [Pronunciation, grammar, or content suggestions]\n\n"
                f"Sample strong response:\n"
                f"{_question.sample_correct_answer}\n\n"
                f"---\n"
                f"You MUST return ONLY a valid JSON object with this exact structure:\n"
                f"{{\n"
                f'  "score": <integer 0-4>,\n'
                f'  "category_scores": {{\n'
                f'    "delivery": <integer 0-4>,\n'
                f'    "language_use": <integer 0-4>,\n'
                f'    "topic_development": <integer 0-4>\n'
                f'  }},\n'
                f'  "feedback": {{\n'
                f'    "summary": "<2-3 sentences overall assessment>",\n'
                f'    "strengths": ["<strength1>", "<strength2>"],\n'
                f'    "improvements": ["<improvement1>", "<improvement2>"],\n'
                f'    "pronunciation_notes": "<specific feedback on pronunciation if applicable>",\n'
                f'    "fluency": "<assessment of pace and flow>"\n'
                f'  }}\n'
                f"}}\n"
                f"Do NOT include any other text, explanation, or markdown formatting. Only the JSON object.")
