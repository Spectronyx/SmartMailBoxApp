from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, MeView, GoogleAuthUrlView, GoogleCallbackView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('google/url/', GoogleAuthUrlView.as_view(), name='google-auth-url'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
]
#