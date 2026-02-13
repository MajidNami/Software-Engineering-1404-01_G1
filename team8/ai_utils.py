import os
import json
import requests
import random
import uuid
import base64
import urllib.parse
import re
import urllib3
from openai import OpenAI, APIError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AIService:
    def __init__(self):
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.gapgpt_api_key = os.environ.get("GAPGPT_API_KEY")
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"

    # ------------------------------------------------------------------------
    # WORD INFO (unchanged)
    # ------------------------------------------------------------------------
    def fetch_word_info(self, word=None, level="A2"):
        if word:
            target = f"the word '{word}'"
            temp_setting = 0.5
        else:
            topics = ["technology", "emotions", "business", "nature", "travel", "philosophy", "arts", "science", "daily life"]
            letters = "abcdefghlmnoprstuvw"
            random_topic = random.choice(topics)
            random_letter = random.choice(letters)
            target = f"a random, useful {level} level English vocabulary word related to '{random_topic}' or starting with the letter '{random_letter}'"
            temp_setting = 1.1

        system_prompt = (
            f"You are an English teacher. Provide details for {target} in strict JSON format. "
            "Use these keys: 'word', 'ipa', 'definition', 'synonyms', 'antonyms', 'collocations', 'examples'. "
            "Synonyms, antonyms, collocations, and examples MUST be arrays of strings."
        )
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": temp_setting
        }
        headers = {"Authorization": f"Bearer {self.groq_api_key}", "Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, json=payload, timeout=45, verify=False)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    # ------------------------------------------------------------------------
    # MNEMONIC + STORY (unchanged)
    # ------------------------------------------------------------------------
    def generate_mnemonic_story(self, word):
        system_prompt = (
            f"You are a creative memory expert. For the English word '{word}', "
            "create a SHORT, VIVID visual mnemonic (max 8 words) and a short memory story (2‑3 sentences). "
            "Also extract a SINGLE, CLEAR image prompt (max 8 words) that would generate a perfect illustration of the mnemonic. "
            "Return valid JSON with keys: 'mnemonic_text', 'story_text', 'image_prompt'."
        )
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.8
        }
        headers = {"Authorization": f"Bearer {self.groq_api_key}", "Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, json=payload, timeout=45, verify=False)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)

    # ------------------------------------------------------------------------
    # IMAGE PROMPT EXTRACTION (unchanged)
    # ------------------------------------------------------------------------
    def extract_image_prompt(self, mnemonic_text, word):
        """Convert a full mnemonic sentence into a short, keyword‑rich prompt."""
        first_sent = mnemonic_text.split('.')[0]
        stopwords = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'of', 'in', 'on', 'at', 'and', 'or', 'with', 'for', 'to', 'it', 'they', 'them', 'this', 'that'}
        words = re.findall(r'\b[a-zA-Z]+\b', first_sent.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        if word.lower() not in keywords:
            keywords.insert(0, word.lower())
        return ' '.join(keywords[:6])

    # ------------------------------------------------------------------------
    # ✅ GAPGPT IMAGE GENERATOR – OFFICIAL (With Debug & Fallback)
    # ------------------------------------------------------------------------
    def generate_image(self, prompt, word):
        """
        Uses the official OpenAI client structure for GapGPT.
        Includes full debug prints and a safe fallback on ANY error.
        """
        print(f"🐞 DEBUG: Starting generate_image for word: '{word}'")

        # 1. Check API Key
        if not self.gapgpt_api_key:
            print("🐞 DEBUG: No GapGPT API key found in environment.")
            return self._fallback_placeholder(word)

        # 2. Check Library Installation
        try:
            from openai import OpenAI
        except ImportError:
            print("🐞 DEBUG: CRITICAL - 'openai' library is not installed. Run 'pip install openai'.")
            return self._fallback_placeholder(word)

        # 3. Try to Generate Image
        try:
            print("🐞 DEBUG: Initializing OpenAI client for GapGPT...")
            client = OpenAI(
                base_url="https://api.gapgpt.app/v1",
                api_key=self.gapgpt_api_key
            )

            # Construct prompt safely
            final_prompt = f"{word}, {prompt[:300]}" # Ensure prompt isn't too long
            print(f"🐞 DEBUG: Sending request... Model: gapgpt/z-image | Prompt: {final_prompt}")

            # --- THE OFFICIAL CALL ---
            response = client.images.generate(
                model="gapgpt/z-image",
                prompt=final_prompt,
                size="1024x1024"
            )
            # -------------------------

            # Extract URL
            if response.data and len(response.data) > 0:
                image_url = response.data[0].url
                print(f"🐞 DEBUG: ✅ Success! Image URL received: {image_url}")
                return image_url
            else:
                print("🐞 DEBUG: ⚠️ Response received but 'data' was empty.")
                return self._fallback_placeholder(word)

        except Exception as e:
            # 4. Catch ANY error (503, 500, Timeout, Auth, etc.)
            print(f"🐞 DEBUG: ❌ GapGPT Failed. Reason: {e}")
            print("🐞 DEBUG: Switching to fallback placeholder.")
            return self._fallback_placeholder(word)
    # ------------------------------------------------------------------------
    # FALLBACK PLACEHOLDER (unique, always works)
    # ------------------------------------------------------------------------
    def _fallback_placeholder(self, word):
        """Unique placeholder – only used when all else fails."""
        colors = ['ff8a65', '6c5ce7', '00b894', '0984e3', 'd63031', 'e84393']
        bg = random.choice(colors)
        rand = random.randint(1, 999999)
        return f"https://placehold.co/512x512/{bg}/white?text={word}&font=montserrat&r={rand}"

    # ------------------------------------------------------------------------
    # PRACTICE SET (unchanged)
    # ------------------------------------------------------------------------
    def generate_practice_set(self, word):
        prompt = f"""
        Generate 4 English practice exercises for the word: "{word}".
        Return ONLY a JSON object with a key "exercises" containing an array of 4 objects.
        The array must follow this order: 
        1. Meaning (Multiple Choice)
        2. Context (Multiple Choice)
        3. Collocation (Multiple Choice)
        4. Sentence (Multiple Choice)

        Format:
        {{
        "exercises": [
            {{
            "question": "What is the meaning of '{word}'?",
            "options": ["option1", "option2", "option3", "option4"],
            "answer": "correct_option"
            }},
            ...
        ]
        }}
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        headers = {"Authorization": f"Bearer {self.groq_api_key}", "Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, json=payload, timeout=45, verify=False)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']