from django.contrib.auth import get_user_model


def get_guest_user():
    """Return a shared guest user for unauthenticated requests in this microservice."""
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='guest_listening',
        defaults={'is_active': True},
    )
    if created:
        user.set_unusable_password()
        user.save()
    return user
