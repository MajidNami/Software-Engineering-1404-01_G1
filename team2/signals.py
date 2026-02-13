from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User
from .models import UserDetails


@receiver(post_save, sender=User)
def create_user_details(sender, instance, created, using=None, **kwargs):
    
    if created:
        try:
            UserDetails.objects.using('team2').get_or_create(
                user_id=instance.id,
                defaults={
                    'email': instance.email,
                    'role': 'student',
                }
            )
        except Exception as e:
            print(f"خطا در ایجاد UserDetails: {str(e)}")


@receiver(post_save, sender=User)
def update_user_details(sender, instance, created, using=None, **kwargs):
    if not created:
        try:
            user_details = UserDetails.objects.using('team2').get(user_id=instance.id)
            if user_details.email != instance.email:
                user_details.email = instance.email
                user_details.save(using='team2')
        except UserDetails.DoesNotExist:
            try:
                UserDetails.objects.using('team2').create(
                    user_id=instance.id,
                    email=instance.email,
                    role='student'
                )
            except Exception:
                pass
