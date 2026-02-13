from django.apps import AppConfig


class Team2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team2'

    def ready(self):
        import team2.signals
