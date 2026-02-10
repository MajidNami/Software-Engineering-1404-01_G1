from django.db import models

class ReadingMaterial(models.Model):
    user_id = models.IntegerField() 
    title = models.CharField(max_length=200)
    content = models.TextField() 
    category = models.CharField(max_length=50) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title