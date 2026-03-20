from django.db import models

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extends the built-in Django User with Google OAuth tokens.
    Created automatically when a user connects their Google account.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_access_token = models.TextField(null=True, blank=True)
    google_refresh_token = models.TextField(null=True, blank=True)
    google_token_expiry = models.DateTimeField(null=True, blank=True)
    google_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"
