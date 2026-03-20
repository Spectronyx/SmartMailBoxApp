"""
URL configuration for the Email app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailViewSet

# Create a router and register the viewset
router = DefaultRouter()
router.register(r'emails', EmailViewSet, basename='email')

urlpatterns = [
    path('', include(router.urls)),
]
