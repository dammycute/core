from django.apps import AppConfig


class ProperConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proper'


    def ready(self):
        import proper.signals