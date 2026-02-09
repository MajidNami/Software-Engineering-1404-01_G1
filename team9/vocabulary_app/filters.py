import django_filters
from datetime import date
from .models import Word


class WordFilter(django_filters.FilterSet):
    """
    Custom filter for Word model with advanced filtering capabilities.
    """
    
    # Exact match filters
    lesson = django_filters.NumberFilter(field_name='lesson__id')
    is_learned = django_filters.BooleanFilter(field_name='is_learned')
    current_day = django_filters.NumberFilter(field_name='current_day')
    
    # Custom filter for "Today's Reviews"
    today_review = django_filters.BooleanFilter(method='filter_today_review')
    
    class Meta:
        model = Word
        fields = ['lesson', 'is_learned', 'current_day', 'today_review']
    
    def filter_today_review(self, queryset, name, value):
        """
        Filter words that are due for review today.
        
        Returns words where:
        - next_review_date <= today
        - is_learned = False
        
        Args:
            queryset: The initial queryset
            name: The filter field name
            value: Boolean value (True to apply filter, False to skip)
        
        Returns:
            Filtered queryset
        """
        if value:
            today = date.today()
            return queryset.filter(
                next_review_date__lte=today,
                is_learned=False
            )
        return queryset
