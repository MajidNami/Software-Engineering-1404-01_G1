from django.db import models

class TestModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'team3'
        db_table = 'team3_testmodel'  # Optional: custom table name

    def __str__(self):
        return self.name


# Add another model for testing relationships
class RelatedModel(models.Model):
    test = models.ForeignKey(TestModel, on_delete=models.CASCADE, related_name='related_items')
    value = models.IntegerField(default=0)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'team3'