from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ListeningItem


@receiver([post_save, post_delete], sender=ListeningItem)
def update_test_total_items(sender, instance, **kwargs):
    instance.test.total_items = instance.test.items.count()
    instance.test.save(update_fields=['total_items'])
