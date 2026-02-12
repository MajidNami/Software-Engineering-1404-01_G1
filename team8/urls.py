from django.urls import path
from django.views.generic import RedirectView, TemplateView
from . import views
from .views import analysis_views
from .views.wordcard import WordCardView 
from .views.mnemonic_views import get_mnemonic
from .views import tts_views  
# --- Add this import ---
from .views.practice_views import PracticeView, SavePracticeResultView 

urlpatterns = [
    path("", RedirectView.as_view(url="wordcard/", permanent=False), name="index"),
    path("ping/", views.ping),
    
    # Main Pages
    path("wordcard/", WordCardView.as_view(), name="wordcard"),
    path('analysis/', analysis_views.text_analysis_page, name='analysis_page'),
    
    # Placeholder for Mnemonics (still a placeholder for now)
    path('mnemonics/', TemplateView.as_view(template_name="team8/mnemonic_page.html"), name='mnemonics'),
    
    # --- UPDATED: Practice Page now uses your real View ---
    path('practice/', PracticeView.as_view(), name='practice'),

    # APIs
    path('api/reading-history/', analysis_views.api_get_history, name='api_history'),
    path('api/text-analysis/', analysis_views.api_perform_analysis, name='api_run_analysis'),
    path('api/get-mnemonic/', get_mnemonic, name='api_mnemonic'),
    path('api/tts/', tts_views.generate_speech, name='tts_generate'),
    
    # --- NEW: API to save practice results ---
    path('api/save-practice/', SavePracticeResultView.as_view(), name='save_practice'),
]