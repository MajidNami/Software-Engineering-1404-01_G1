import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from core.auth import api_login_required 
from team8.models import LearningWord, PracticeSession
from team8.ai_utils import AIService

@method_decorator(api_login_required, name='dispatch')
class PracticeView(View):
    template_name = "team8/practice_page.html"
    ai_service = AIService()

    def get(self, request):
        return render(request, self.template_name, {"active_tab": "practice"})

    def post(self, request):
        user_id = str(request.user.id)
        latest_word = LearningWord.objects.filter(user_id=user_id).order_by('-created_at').first()
        
        if not latest_word:
            return JsonResponse({"status": "error", "message": "No word found. Generate a card first!"})

        try:
            raw_data = self.ai_service.generate_adaptive_practice(latest_word.word)
            return JsonResponse({"status": "success", "data": json.loads(raw_data)})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

@method_decorator(api_login_required, name='dispatch')
class SavePracticeResultView(View):
    def post(self, request):
        data = json.loads(request.body)
        word_text = data.get('word')
        user_id = str(request.user.id)
        
        word_obj = LearningWord.objects.filter(user_id=user_id, word=word_text.lower()).first()
        if word_obj:
            PracticeSession.objects.create(word=word_obj, user_id=user_id)
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error"}, status=400)