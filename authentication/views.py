import random
import string
import pytz
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, get_user_model
from django.conf import settings
from django.db import IntegrityError
from django.core.cache import caches
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from utilities.error_handler import render_errors
from . import serializers as CustomSerializers

User = get_user_model()

# Cache instances
email_verification_cache = caches['email_verification']
password_reset_cache = caches['password_reset']
password_tries_cache = caches['password_tries']
password_attempts_cache = caches['password_attempts']


def generate_pin():
    return str(random.randint(100000, 999999))

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=64))


def send_verification_email(user):
    """Send a verification PIN to user’s email."""
    pin = generate_pin()
    send_mail(
        'Dharmzeey Shop Email Verification',
        f'Hello 👋,\nYour verification PIN is {pin}.\nIt expires in 10 minutes.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    email_verification_cache.set(
        f"email_verification:{user.email}",
        {'email_pin': pin, 'timestamp': datetime.now(pytz.UTC).timestamp()},
        timeout=600  # 10 mins
    )


# ---------------------- AUTH VIEWS ----------------------

class UserCreateView(APIView):
    def post(self, request):
        serializer = CustomSerializers.UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": render_errors(serializer.errors)}, status=400)

        try:
            user = serializer.save()
            send_verification_email(user)
            tokens = RefreshToken.for_user(user)
            login(request, user, backend="authentication.backends.EmailOrPhoneBackend")

            return Response({
                'access_token': str(tokens.access_token),
                'refresh_token': str(tokens),
                'data': CustomSerializers.UserSerializer(user).data
            }, status=201)
        except IntegrityError:
            return Response(
                {'error': 'User with this email or phone number already exists.'},
                status=409
            )
user_create = UserCreateView.as_view()


class UserLoginView(APIView):
    def post(self, request):
        serializer = CustomSerializers.UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": render_errors(serializer.errors)}, status=400)

        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone_number')
        password = serializer.validated_data['password']

        user = authenticate(request=request, email=email, phone_number=phone, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        login(request, user, backend="authentication.backends.EmailOrPhoneBackend")
        tokens = RefreshToken.for_user(user)

        return Response({
            "access_token": str(tokens.access_token),
            "refresh_token": str(tokens),
        }, status=200)
user_login = UserLoginView.as_view()


# ---------------------- EMAIL VERIFICATION ----------------------

class SendEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response({"message": "Email already verified"}, status=200)

        if email_verification_cache.get(f"email_verification:{user.email}"):
            return Response({"error": "PIN already sent"}, status=409)

        send_verification_email(user)
        return Response({"message": "Verification PIN sent to your email"}, status=200)
send_email_verificiation = SendEmailVerificationView.as_view()


class VerifyEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CustomSerializers.EmailVeriificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": render_errors(serializer.errors)}, status=400)

        user = request.user
        cached = email_verification_cache.get(f"email_verification:{user.email}")

        if not cached:
            return Response({"error": "PIN expired or not sent"}, status=400)

        if cached['email_pin'] != serializer.validated_data['email_pin']:
            return Response({"error": "Invalid PIN"}, status=403)

        user.email_verified = True
        user.save()
        email_verification_cache.delete(f"email_verification:{user.email}")
        return Response({"message": "Email verified successfully"}, status=200)
verify_email = VerifyEmailView.as_view()


# ---------------------- PASSWORD RESET ----------------------

class RequestPasswordResetView(APIView):
    """Step 1: Request reset PIN via email"""

    def post(self, request):
        serializer = CustomSerializers.RequestPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": render_errors(serializer.errors)}, status=400)

        email = serializer.validated_data['email'].lower()
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            # Hide user existence for security
            return Response({"message": "If the email exists, a reset code has been sent."}, status=200)

        # Limit excessive requests
        tries = password_tries_cache.get(f"tries:{email}", 0)
        if tries >= 3:
            return Response({"error": "Too many attempts. Try again later."}, status=429)

        pin = generate_pin()
        reset_token = generate_token()

        send_mail(
            'Dharmzeey Shop Password Reset',
            f'Use this PIN to reset your password: {pin}.\nIt expires in 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        password_reset_cache.set(
            f"reset:{email}",
            {'email_pin': pin, 'token': reset_token, 'timestamp': datetime.now(pytz.UTC).timestamp()},
            timeout=600
        )
        password_tries_cache.set(f"tries:{email}", tries + 1, timeout=86400)

        return Response({"message": "If the email exists, a reset code has been sent."}, status=200)
request_password_reset = RequestPasswordResetView.as_view()


class ResetPasswordView(APIView):
    """Step 2: Verify the PIN"""

    def post(self, request):
        serializer = CustomSerializers.PasswordResetVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": render_errors(serializer.errors)}, status=400)

        email = serializer.validated_data['email']
        pin = serializer.validated_data['email_pin']
        password = serializer.validated_data['password']
        token = serializer.validated_data['reset_token']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Always respond with a generic message to avoid leaking user existence
            return Response({"error": "Session expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Trial limit check
        trials = password_attempts_cache.get(f"password_attempts:{email}")
        if trials is None:
            password_attempts_cache.set(f"password_attempts:{email}", 0, timeout=86400)
        elif trials >= 5:
            return Response({"error": "Too many attempts. Try again after 24 hours."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        password_attempts_cache.set(f"password_attempts:{email}", (trials or 0) + 1, timeout=86400)

        cached = password_reset_cache.get(f"password_reset:{email}")
        if not cached:
            return Response({"error": "Session expired"}, status=status.HTTP_400_BAD_REQUEST)

        if cached['email_pin'] != pin or cached['reset_token'] != token:
            return Response({"error": "Invalid PIN"}, status=status.HTTP_400_BAD_REQUEST)

        if (datetime.now(pytz.UTC).timestamp() - cached['timestamp']) > 600:
            password_reset_cache.delete(f"password_reset:{email}")
            return Response({"error": "PIN expired"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            password_reset_cache.delete(f"password_reset:{email}")
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Always respond with a generic message to avoid leaking user existence
            return Response({"error": "Session expired"}, status=status.HTTP_400_BAD_REQUEST)
reset_password = ResetPasswordView.as_view()


# ---------------------- LOGOUT ----------------------

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=205)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)
logout = LogoutView.as_view()