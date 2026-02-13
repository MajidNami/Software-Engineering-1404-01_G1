from django.db import models

class PracticeSession(models.Model):
    # Link to the word being practiced
    word = models.ForeignKey('LearningWord', on_delete=models.CASCADE, related_name='sessions')
    user_id = models.CharField(max_length=255, db_index=True)
    
    # Track completion
    is_completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'team8'