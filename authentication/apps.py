from django.apps import AppConfig
from django.db.models.signals import post_save

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

    def ready(self):
        from django.contrib.auth.models import User
        from .models import UserProfile

        # Automatically create a profile when a new user is created
        def create_user_profile(sender, instance, created, **kwargs):
            if created:
                UserProfile.objects.create(user=instance)

        post_save.connect(create_user_profile, sender=User)