from django.apps import AppConfig


class ListeningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listening'
    verbose_name = 'TOEFL Listening'

    def ready(self):
        import listening.signals  # noqa: F401
