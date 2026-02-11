from django.db import models
from django.utils import timezone
from datetime import date, timedelta

# Create your models here.


class Lesson(models.Model):
    # User ID retrieved from the Core service cookies
    user_id = models.IntegerField() 
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (User: {self.user_id})"
    
    @property
    def progress_percent(self):
        """
        Calculate lesson progress based on actual ticks achieved.
        
        Progress is calculated as:
        (actual_ticks / total_possible_ticks) * 100
        
        Where:
        - total_possible_ticks = number of words * 6 (6 ticks = 100% per word)
        - actual_ticks = sum of all '1' characters in review_history
        
        Returns:
            float: Progress percentage rounded to 1 decimal place, capped at 100%.
        """
        words = self.words.all()
        word_count = words.count()
        
        # Handle empty lesson (division by zero)
        if word_count == 0:
            return 0.0
        
        # Total possible ticks (6 ticks per word = 100%)
        total_possible_ticks = word_count * 6
        
        # Calculate actual ticks by counting '1's in all review_history fields
        actual_ticks = sum(
            word.review_history.count('1') for word in words
        )
        
        # Calculate progress percentage
        progress = (actual_ticks / total_possible_ticks) * 100
        
        # Cap at 100% and round to 1 decimal place
        return round(min(progress, 100.0), 1)

class Word(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='words')
    term = models.CharField(max_length=100) # English word
    definition = models.TextField()        # Persian translation
    
    # --- 8-Tick Logic ---
    # Current review day (from 1 to 8)
    current_day = models.IntegerField(default=0) 
    
    # Stores ticks and crosses as an 8-character string (e.g., '11010000')
    review_history = models.CharField(max_length=8, default='00000000')
    
    # Final learning status (True if 6 ticks are achieved)
    is_learned = models.BooleanField(default=False)
    
    # To prevent multiple reviews on the same day
    last_review_date = models.DateField(null=True, blank=True)
    
    # Next scheduled review date based on spaced repetition
    next_review_date = models.DateField(default=date.today)

    def __str__(self):
        return self.term
    
    def perform_review(self, is_correct):
        """
        Execute the 8-Tick Leitner review logic with spaced repetition.
        
        Args:
            is_correct (bool): Whether the user answered correctly.
        
        Returns:
            dict: Status dictionary with success flag and message.
        """
        today = date.today()
        
        # Check if already reviewed today
        if self.last_review_date == today:
            return {
                'success': False,
                'message': 'Word already reviewed today'
            }
        
        # Ensure current_day is within valid range
        if self.current_day >= 8:
            return {
                'success': False,
                'message': 'Word has completed all 8 review days'
            }
        
        # Update review_history at the current_day index
        history_list = list(self.review_history)
        history_list[self.current_day] = '1' if is_correct else '0'
        self.review_history = ''.join(history_list)
        
        # Increment current_day
        self.current_day += 1
        
        # Calculate next_review_date based on spaced repetition intervals
        if is_correct:
            # Spaced repetition intervals by day (box number)
            intervals = {
                1: 1,   # Day 1: +1 day
                2: 2,   # Day 2: +2 days
                3: 4,   # Day 3: +4 days
                4: 8,   # Day 4: +8 days
                5: 16,  # Day 5: +16 days
                6: 32,  # Day 6: +32 days
                7: 64,  # Day 7: +64 days
                8: None # Day 8: Learned (no next review)
            }
            
            interval_days = intervals.get(self.current_day)
            if interval_days is not None:
                self.next_review_date = today + timedelta(days=interval_days)
            else:
                # Day 8 - no next review needed
                self.next_review_date = None
        else:
            # If incorrect, schedule for tomorrow
            self.next_review_date = today + timedelta(days=1)
        
        # Check if learning is complete (current_day reached 8)
        if self.current_day == 8:
            # Count the number of '1's (correct answers)
            correct_count = self.review_history.count('1')
            if correct_count >= 6:
                self.is_learned = True
                self.next_review_date = None  # No more reviews needed
        
        # Update last_review_date to today
        self.last_review_date = today
        
        # Save the changes
        self.save()
        
        return {
            'success': True,
            'message': 'Review recorded successfully',
            'current_day': self.current_day,
            'review_history': self.review_history,
            'is_learned': self.is_learned,
            'next_review_date': self.next_review_date
        }