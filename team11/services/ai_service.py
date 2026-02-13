"""
AI Assessment Service for TOEFL Writing and Speaking Tasks

This module provides functions to assess writing and speaking submissions
using AI APIs (Deepseek for text analysis, Whisper for audio transcription).
"""

import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from .prompts import (
    WRITING_SYSTEM_PROMPT,
    WRITING_USER_PROMPT_TEMPLATE,
    SPEAKING_SYSTEM_PROMPT,
    SPEAKING_USER_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "https://api.gapgpt.app/v1"
API_KEY = "sk-NQIf9DDM88vlR7to5iys8BFQYwlHTvbtKZeVlwMawdEMOk61"

# Initialize OpenAI client with a timeout to avoid hanging requests
client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY, timeout=300.0)

# Model names
DEEPSEEK_MODEL = "deepseek-chat"
WHISPER_MODEL = "whisper-1"


def assess_writing(topic: str, text_body: str, word_count: int) -> Dict[str, Any]:
    """
    Assess a writing submission using Deepseek AI.
    
    Args:
        topic: The writing prompt/topic
        text_body: The submitted text
        word_count: Number of words in the submission
        
    Returns:
        Dict containing assessment results with keys:
            - overall_score: float (0-100)
            - grammar_score: float (0-100)
            - vocabulary_score: float (0-100)
            - coherence_score: float (0-100)
            - fluency_score: float (0-100)
            - feedback_summary: str
            - suggestions: list of str
            - success: bool
            - error: str (if success=False)
    """
    try:
        # Prepare the user prompt with actual data
        user_prompt = WRITING_USER_PROMPT_TEMPLATE.format(
            topic=topic,
            text_body=text_body,
            word_count=word_count
        )
        
        logger.info(f"Assessing writing submission: {word_count} words")
        
        # Make API call with system and user prompts
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": WRITING_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Low temperature for consistent scoring
            max_tokens=1000,
        )
        
        # Extract the response content
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            assessment = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
                assessment = json.loads(content)
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
                assessment = json.loads(content)
            else:
                raise
        
        # Validate required fields
        required_fields = [
            'overall_score', 'grammar_score', 'vocabulary_score',
            'coherence_score', 'fluency_score', 'feedback_summary', 'suggestions'
        ]
        
        for field in required_fields:
            if field not in assessment:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure scores are floats
        for score_field in ['overall_score', 'grammar_score', 'vocabulary_score', 
                           'coherence_score', 'fluency_score']:
            assessment[score_field] = float(assessment[score_field])
        
        # Ensure suggestions is a list
        if not isinstance(assessment['suggestions'], list):
            assessment['suggestions'] = [assessment['suggestions']]
        
        assessment['success'] = True
        logger.info(f"Writing assessment completed: overall_score={assessment['overall_score']}")
        
        return assessment
        
    except APIConnectionError as e:
        logger.error(f"API Connection Error: {e}")
        return {
            'success': False,
            'error': 'Failed to connect to AI service. Please try again later.',
            'overall_score': None
        }
    except RateLimitError as e:
        logger.error(f"Rate Limit Error: {e}")
        return {
            'success': False,
            'error': 'Too many requests. Please wait a moment and try again.',
            'overall_score': None
        }
    except APIError as e:
        logger.error(f"API Error: {e}")
        return {
            'success': False,
            'error': f'AI service error: {str(e)}',
            'overall_score': None
        }
    except Exception as e:
        logger.error(f"Unexpected error in assess_writing: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'Assessment failed: {str(e)}',
            'overall_score': None
        }


def transcribe_audio(audio_file_path: str) -> Dict[str, Any]:
    """
    Transcribe audio file using Whisper API.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Dict containing:
            - transcription: str (the transcribed text)
            - success: bool
            - error: str (if success=False)
    """
    try:
        logger.info(f"Transcribing audio file: {audio_file_path}")
        
        # Open and transcribe the audio file
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file
            )
        
        transcription = response.text.strip()
        
        if not transcription:
            return {
                'success': False,
                'error': 'No speech detected in the audio file.',
                'transcription': None
            }
        
        logger.info(f"Transcription completed: {len(transcription)} characters")
        
        return {
            'success': True,
            'transcription': transcription
        }
        
    except FileNotFoundError:
        logger.error(f"Audio file not found: {audio_file_path}")
        return {
            'success': False,
            'error': 'Audio file not found.',
            'transcription': None
        }
    except APIConnectionError as e:
        logger.error(f"API Connection Error: {e}")
        return {
            'success': False,
            'error': 'Failed to connect to transcription service.',
            'transcription': None
        }
    except APIError as e:
        logger.error(f"API Error: {e}")
        return {
            'success': False,
            'error': f'Transcription service error: {str(e)}',
            'transcription': None
        }
    except Exception as e:
        logger.error(f"Unexpected error in transcribe_audio: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'Transcription failed: {str(e)}',
            'transcription': None
        }


def assess_speaking(topic: str, audio_file_path: str, duration_seconds: int) -> Dict[str, Any]:
    """
    Assess a speaking submission using Whisper (transcription) + Deepseek (assessment).
    
    This is a two-step process:
    1. Transcribe the audio using Whisper
    2. Assess the transcription using Deepseek
    
    Args:
        topic: The speaking prompt/topic
        audio_file_path: Path to the audio file
        duration_seconds: Duration of the recording
        
    Returns:
        Dict containing assessment results with keys:
            - overall_score: float (0-100)
            - pronunciation_score: float (0-100)
            - fluency_score: float (0-100)
            - vocabulary_score: float (0-100)
            - grammar_score: float (0-100)
            - coherence_score: float (0-100)
            - feedback_summary: str
            - suggestions: list of str
            - transcription: str (the transcribed text)
            - success: bool
            - error: str (if success=False)
    """
    try:
        # Step 1: Transcribe the audio
        transcription_result = transcribe_audio(audio_file_path)
        
        if not transcription_result['success']:
            return {
                'success': False,
                'error': transcription_result['error'],
                'overall_score': None,
                'transcription': None
            }
        
        transcription = transcription_result['transcription']
        
        # Step 2: Assess the transcription
        user_prompt = SPEAKING_USER_PROMPT_TEMPLATE.format(
            topic=topic,
            transcription=transcription,
            duration_seconds=duration_seconds
        )
        
        logger.info(f"Assessing speaking submission: {duration_seconds}s audio")
        
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SPEAKING_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            assessment = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
                assessment = json.loads(content)
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
                assessment = json.loads(content)
            else:
                raise
        
        # Validate required fields
        required_fields = [
            'overall_score', 'pronunciation_score', 'fluency_score',
            'vocabulary_score', 'grammar_score', 'coherence_score',
            'feedback_summary', 'suggestions'
        ]
        
        for field in required_fields:
            if field not in assessment:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure scores are floats
        for score_field in ['overall_score', 'pronunciation_score', 'fluency_score',
                           'vocabulary_score', 'grammar_score', 'coherence_score']:
            assessment[score_field] = float(assessment[score_field])
        
        # Ensure suggestions is a list
        if not isinstance(assessment['suggestions'], list):
            assessment['suggestions'] = [assessment['suggestions']]
        
        # Add transcription to the result
        assessment['transcription'] = transcription
        assessment['success'] = True
        
        logger.info(f"Speaking assessment completed: overall_score={assessment['overall_score']}")
        
        return assessment
        
    except APIConnectionError as e:
        logger.error(f"API Connection Error: {e}")
        return {
            'success': False,
            'error': 'Failed to connect to AI service. Please try again later.',
            'overall_score': None,
            'transcription': None
        }
    except RateLimitError as e:
        logger.error(f"Rate Limit Error: {e}")
        return {
            'success': False,
            'error': 'Too many requests. Please wait a moment and try again.',
            'overall_score': None,
            'transcription': None
        }
    except APIError as e:
        logger.error(f"API Error: {e}")
        return {
            'success': False,
            'error': f'AI service error: {str(e)}',
            'overall_score': None,
            'transcription': None
        }
    except Exception as e:
        logger.error(f"Unexpected error in assess_speaking: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'Assessment failed: {str(e)}',
            'overall_score': None,
            'transcription': None
        }
