from django.db import models
from django.conf import settings


class ReadingMaterial(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='readings'
    )    
    title = models.CharField(max_length=200)
    content = models.TextField() 
    category = models.CharField(max_length=50) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title