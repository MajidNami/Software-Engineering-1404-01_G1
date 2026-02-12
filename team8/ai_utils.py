import os
import requests
import json
import urllib3
class AIService:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.model = "llama-3.1-8b-instant" 

    def fetch_word_info(self, word=None, level="A1"):
        target = f"the word '{word}'" if word else f"a random useful {level} level English vocabulary word"
        
        system_prompt = (
            f"You are an English teacher. Provide details for {target} in strict JSON format. "
            "Use these keys: 'word', 'ipa', 'definition', 'synonyms', 'antonyms', 'collocations', 'examples'. "
            "Synonyms, antonyms, collocations, and examples MUST be arrays of strings."
        )

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.5
        }

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        response = requests.post(self.url, headers=headers, json=payload, timeout=45,verify=False)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def generate_mnemonic_story(self, word):
        """
        Uses Groq API to generate a visual mnemonic description and a memory story.
        Returns a dict with 'mnemonic_text' and 'story_text'.
        """
        system_prompt = (
            f"You are a creative memory expert. For the English word '{word}', "
            "create a short, vivid visual mnemonic (max 2 sentences) and a short memory story (2-3 sentences). "
            "Return valid JSON with keys: 'mnemonic_text' and 'story_text'."
        )
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.8
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, json=payload, timeout=45, verify=False)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)

    def generate_image_hf(self, prompt):
        print("🔵 generate_image_hf CALLED with prompt:", prompt)   # <-- 1
        
        import urllib.parse
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
            print("🟢 Generated Pollinations URL:", image_url)      # <-- 2
            return image_url
        except Exception as e:
            print("🔴 Exception in generate_image_hf:", e)          # <-- 3
            fallback = "https://cataas.com/cat"
            print("🟡 Using fallback:", fallback)
            return fallback
