import requests
import json

class AIService:
    def __init__(self):
        # this finds the key from my .env file 
        self.api_key = os.environ.get("GROQ_API_KEY", "default_if_not_found")
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile" # Or "llama3-8b-8192"

    def fetch_word_info(self, word):
        """
        Calls Groq API to get detailed linguistic information about a word.
        Returns a dictionary formatted for the WordCard model.
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": application/json"
        }

        # The System Prompt ensures the AI returns ONLY clean JSON
        system_prompt = (
            "You are a professional English language teacher. "
            "Provide details for the given word in strict JSON format. "
            "The JSON must have these keys: 'ipa', 'synonyms', 'antonyms', 'collocations', 'examples'. "
            "The 'examples' key must be a list of 2 strings. "
            "Do not include any conversational text or markdown blocks, only raw JSON."
        )

        user_prompt = f"Provide details for the word: '{word}'"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"}, # Groq supports JSON mode
            "temperature": 0.5
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=10)
            response.raise_for_status() # Raise error for bad status codes
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse the string content into a Python Dictionary
            data = json.loads(content)
            
            # Ensure all keys exist to avoid errors in views.py
            return {
                "ipa": data.get("ipa", ""),
                "synonyms": data.get("synonyms", ""),
                "antonyms": data.get("antonyms", ""),
                "collocations": data.get("collocations", ""),
                "examples": data.get("examples", [])
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Groq API Connection Error: {str(e)}")
        except (KeyError, json.JSONDecodeError):
            raise Exception("Groq returned an invalid response format.")