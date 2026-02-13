import json
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils import timezone  # <--- Added this import
from core.auth import api_login_required 

from team8.models import LearningWord
from team8.ai_utils import AIService

@method_decorator(api_login_required, name='dispatch')
class WordCardView(View):
    template_name = "team8/wordcard_page.html"
    ai_service = AIService()

    def get(self, request):
        """Renders the HTML page"""
        return render(request, self.template_name, {"active_tab": "wordcard"})

    def post(self, request):
        """Handles AI generation requests"""
        word_text = request.POST.get("word") # Can be empty for random
        user_id = str(request.user.id)

        try:
            # 1. Get JSON from AI
            raw_data = self.ai_service.fetch_word_info(word_text)
            data = json.loads(raw_data)

            # 2. Save/Update in DB
            # We use get_or_create to avoid duplicate words for the same user
            word_obj, created = LearningWord.objects.get_or_create(
                user_id=user_id, 
                word=data['word'].lower(),
                defaults={
                    'ipa_pronunciation': data.get('ipa', ''),
                    'definition': data.get('definition', ''),
                    'synonyms': ", ".join(data.get('synonyms', [])),
                    'antonyms': ", ".join(data.get('antonyms', [])),
                    'collocations': ", ".join(data.get('collocations', [])),
                    'example_sentences': "\n".join(data.get('examples', []))
                }
            )

            # --- FIX FOR THE PRACTICE PAGE ---
            # If the word was NOT created (it already existed), we update its 
            # timestamp to 'now'. This forces it to be the "latest" word 
            # in your history, so the Practice page picks it up correctly.
            if not created:
                word_obj.created_at = timezone.now()
                word_obj.save()
            # ---------------------------------

            return JsonResponse({"status": "success", "data": data})
            
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=500)