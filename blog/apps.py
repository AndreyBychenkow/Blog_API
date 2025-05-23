from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Блог'
    
    def ready(self):
        """
        Импортируем сигналы при старте приложения
        """
        import blog.signals
