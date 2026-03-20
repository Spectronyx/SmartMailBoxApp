from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.conf import settings
import logging

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import UserProfile

logger = logging.getLogger(__name__)


def _get_tokens(user):
    """Return JWT access + refresh tokens for a given user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    """POST /api/auth/register/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = _get_tokens(user)
            return Response({
                'user': UserSerializer(user).data,
                **tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """POST /api/auth/login/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = _get_tokens(user)
            return Response({
                'user': UserSerializer(user).data,
                **tokens
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """GET /api/auth/me/  — returns current user info"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ─────────────────────────────────────────────
# Google OAuth2
# ─────────────────────────────────────────────

class GoogleAuthUrlView(APIView):
    """GET /api/auth/google/url/  — returns the Google consent URL"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .google_oauth import get_auth_url
        url = get_auth_url()
        if not url:
            return Response(
                {'error': 'Google OAuth not configured. Set GOOGLE_OAUTH_CLIENT_ID and SECRET in .env.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response({'url': url})


class GoogleCallbackView(APIView):
    """GET /api/auth/google/callback/?code=...  — exchanges code, saves tokens, links mailbox"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'Missing code parameter'}, status=status.HTTP_400_BAD_REQUEST)

        from .google_oauth import exchange_code
        from mailboxes.models import Mailbox

        token_data = exchange_code(code)
        if not token_data:
            return Response({'error': 'Failed to exchange code with Google'}, status=status.HTTP_400_BAD_REQUEST)

        # Save tokens to UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.google_access_token = token_data['access_token']
        profile.google_refresh_token = token_data.get('refresh_token', '')
        profile.google_email = token_data.get('email', request.user.email)

        if token_data.get('expires_at'):
            from django.utils import timezone
            import datetime
            profile.google_token_expiry = timezone.now() + datetime.timedelta(seconds=token_data['expires_in'])

        profile.save()

        # Create or update Google mailbox linked to this user
        google_email = token_data.get('email', request.user.email)
        mailbox, created = Mailbox.objects.update_or_create(
            email_address=google_email,
            defaults={
                'user': request.user,
                'provider': 'GMAIL',
                'is_active': True,
            }
        )

        return Response({
            'message': 'Google account connected successfully!',
            'google_email': google_email,
            'mailbox_id': mailbox.id,
            'mailbox_created': created
        })
