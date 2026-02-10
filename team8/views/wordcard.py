from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from team8.models import LearningWord
from team8.ai_utils import AIService

class WordCardView(View):
    template_name = 'team8/wordcard.html'
    ai_service = AIService()

    def get(self, request):
        """Display the search page and a list of recently learned words."""
        user_id = request.user.id if request.user.is_authenticated else None
        
        recent_words = []
        if user_id:
            recent_words = LearningWord.objects.filter(user_id=user_id).order_by('-created_at')[:5]

        return render(request, self.template_name, {
            'active_tab': 'wordcard',
            'recent_words': recent_words
        })

    def post(self, request):
        """Handle the AI search/generation."""
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login first'}, status=401)

        word_text = request.POST.get('word', '').strip().lower()
        user_id = request.user.id

        if not word_text:
            return JsonResponse({'error': 'Word field is empty'}, status=400)

        # 1. Database Check (Cache)
        word_obj = LearningWord.objects.filter(user_id=user_id, word=word_text).first()
        
        if word_obj:
            return JsonResponse({
                'status': 'success',
                'source': 'database',
                'data': self._serialize(word_obj)
            })

        # 2. AI Call
        try:
            ai_data = self.ai_service.fetch_word_info(word_text)
            
            # 3. Save to Team 8 Database
            word_obj = LearningWord.objects.create(
                user_id=user_id,
                word=word_text,
                ipa_pronunciation=ai_data['ipa'],
                synonyms=ai_data['synonyms'],
                antonyms=ai_data['antonyms'],
                collocations=ai_data['collocations'],
                example_sentences="\n".join(ai_data['examples'])
            )

            return JsonResponse({
                'status': 'success',
                'source': 'ai_generated',
                'data': self._serialize(word_obj)
            })

        except Exception as e:
            return JsonResponse({'error': f'AI Service failed: {str(e)}'}, status=500)

    def _serialize(self, obj):
        """Helper to format model data for the frontend."""
        return {
            'word': obj.word,
            'ipa': obj.ipa_pronunciation,
            'synonyms': obj.synonyms,
            'antonyms': obj.antonyms,
            'collocations': obj.collocations,
            'examples': obj.example_sentences.split('\n')
        }