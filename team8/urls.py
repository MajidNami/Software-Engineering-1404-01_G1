from django.urls import path
from django.views.generic import RedirectView, TemplateView
from . import views
from .views import analysis_views
from .views.wordcard import WordCardView 
from .views.mnemonic_views import get_mnemonic
from .views import tts_views  

# I am creating simple placeholders for Practice and Mnemonics for now
# You can replace TemplateView with your actual views later.

urlpatterns = [
    path("", RedirectView.as_view(url="wordcard/", permanent=False), name="index"),
    path("ping/", views.ping),
    
    # Main Pages
    path("wordcard/", WordCardView.as_view(), name="wordcard"),
    path('analysis/', analysis_views.text_analysis_page, name='analysis_page'),
    
    # Placeholder pages (so the menu buttons work)
    path('mnemonics/', TemplateView.as_view(template_name="team8/mnemonic_page.html"), name='mnemonics'),
    path('practice/', TemplateView.as_view(template_name="team8/practice_page.html"), name='practice'),

    # APIs
    path('api/reading-history/', analysis_views.api_get_history, name='api_history'),
    path('api/text-analysis/', analysis_views.api_perform_analysis, name='api_run_analysis'),
    path('api/get-mnemonic/', get_mnemonic, name='api_mnemonic'),
    path('api/tts/', tts_views.generate_speech, name='tts_generate'),
]