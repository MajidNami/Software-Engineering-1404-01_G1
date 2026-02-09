import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import date
from .models import Lesson, Word
from .serializers import LessonSerializer, WordSerializer
from .filters import WordFilter

TEAM_NAME = "team9"



@api_login_required
def ping(request):
    # Standard health check for the core system
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    # Renders the main index page
    return render(request, f"{TEAM_NAME}/index.html")

# --- New REST API ViewSets ---

class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Lesson model with search, filtering, and ordering capabilities.
    
    Endpoints:
    - GET /api/lessons/ - List all lessons
    - POST /api/lessons/ - Create new lesson
    - GET /api/lessons/{id}/ - Retrieve specific lesson
    - PUT /api/lessons/{id}/ - Update lesson
    - DELETE /api/lessons/{id}/ - Delete lesson
    
    Query Parameters:
    - search: Search in title and description
    - user_id: Filter by user ID
    - ordering: Order by created_at (e.g., ?ordering=-created_at for descending)
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
    # Enable filter backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search in title and description
    search_fields = ['title', 'description']
    
    # Exact match filtering for user_id
    filterset_fields = ['user_id']
    
    # Allow ordering by created_at
    ordering_fields = ['created_at']
    ordering = ['-created_at']  # Default ordering

class WordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Word model with advanced search, filtering, and ordering.
    
    Endpoints:
    - GET /api/words/ - List all words
    - POST /api/words/ - Create new word
    - GET /api/words/{id}/ - Retrieve specific word
    - PUT /api/words/{id}/ - Update word
    - DELETE /api/words/{id}/ - Delete word
    - POST /api/words/{id}/review/ - Review a word
    
    Query Parameters:
    - search: Search in term (English) and definition (Persian)
    - lesson: Filter by lesson ID (exact match)
    - is_learned: Filter by learned status (true/false)
    - current_day: Filter by current day (0-8)
    - today_review: Filter for today's reviews (true) - words due today and not learned
    - ordering: Order by next_review_date or current_day (e.g., ?ordering=next_review_date)
    
    Legacy Parameter:
    - to_review: Deprecated, use today_review instead
    """
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    
    # Enable filter backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search in both term (English) and definition (Persian)
    search_fields = ['term', 'definition']
    
    # Use custom filter class for advanced filtering
    filterset_class = WordFilter
    
    # Allow ordering by next_review_date and current_day
    ordering_fields = ['next_review_date', 'current_day']
    ordering = ['next_review_date']  # Default ordering
    
    def get_queryset(self):
        """
        Optionally filter words based on query parameters.
        Maintains backward compatibility with legacy 'to_review' parameter.
        """
        queryset = super().get_queryset()
        
        # Legacy support: Handle old 'to_review' parameter
        if self.request.query_params.get('to_review') == 'true':
            # Get user_id from authenticated user (security enhancement)
            user_id = self.request.user.id
            today = date.today()
            
            # Filter words where next_review_date is today or earlier
            queryset = queryset.filter(
                lesson__user_id=user_id,
                current_day__lt=8,
                is_learned=False,
                next_review_date__lte=today
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        Perform a review on a specific word.
        
        Expected payload:
        {
            "is_correct": true/false
        }
        
        Returns the updated word status.
        """
        word = self.get_object()
        is_correct = request.data.get('is_correct')
        
        # Validate input
        if is_correct is None:
            return Response(
                {'error': 'is_correct field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform the review
        result = word.perform_review(is_correct)
        
        if result['success']:
            serializer = self.get_serializer(word)
            return Response({
                'message': result['message'],
                'word': serializer.data,
                'current_day': result['current_day'],
                'review_history': result['review_history'],
                'is_learned': result['is_learned'],
                'next_review_date': result.get('next_review_date')
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )