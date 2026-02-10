from django.db import models

class LearningWord(models.Model):
    user_id = models.IntegerField() # From Core Auth
    word = models.CharField(max_length=100)
    
    ipa_pronunciation = models.CharField(max_length=100, blank=True)
    synonyms = models.TextField(blank=True)
    antonyms = models.TextField(blank=True)
    collocations = models.TextField(blank=True)
    example_sentences = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'team8'
        unique_together = ('user_id', 'word')