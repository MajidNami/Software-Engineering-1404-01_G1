from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from ..models.LearningWord import LearningWord
from ..models.PracticeSession import PracticeSession

@login_required
def analytics_page(request):
    # Match the user_id logic from your wordcard.py
    user_id = str(request.user.id)
    
    # 1. Basic Stats
    total_words = LearningWord.objects.filter(user_id=user_id).count()
    total_practices = PracticeSession.objects.filter(user_id=user_id).count()
    
    # 2. Last 5 Words
    recent_words = LearningWord.objects.filter(user_id=user_id).order_by('-created_at')[:5]

    # 3. Chart Data: Words Learned per Day
    daily_stats = (
        LearningWord.objects.filter(user_id=user_id)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Standard python lists (Django will safely convert these to JSON in the template)
    dates = [str(entry['date']) for entry in daily_stats]
    counts = [entry['count'] for entry in daily_stats]

    context = {
        "total_words": total_words,
        "total_practices": total_practices,
        "recent_words": recent_words,
        "chart_dates": dates,
        "chart_counts": counts,
    }
    
    return render(request, 'team8/analytics_page.html', context)