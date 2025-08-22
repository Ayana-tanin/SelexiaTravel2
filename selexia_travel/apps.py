from django.apps import AppConfig


class SelexiaTravelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'selexia_travel'
    verbose_name = 'SELEXIA Travel'
    
    def ready(self):
        import selexia_travel.signals