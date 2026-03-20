"""
URL configuration for the Mailbox app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MailboxViewSet

# Create a router and register the viewset
router = DefaultRouter()
router.register(r'mailboxes', MailboxViewSet, basename='mailbox')

urlpatterns = [
    path('', include(router.urls)),
]
