from django.apps import AppConfig


class NgosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ngos'


# ngos/apps.py
from django.apps import AppConfig

class NgosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ngos'

    def ready(self):
        import ngos.signals

