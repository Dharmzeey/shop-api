from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class EmailOrPhoneBackend(BaseBackend):
    def authenticate(self, request, email=None, phone_number=None, password=None, **kwargs):
        logger.debug(f"Authenticating with email: {email}, phone_number: {phone_number}")
        try:
            user = User.objects.get(Q(email=email) | Q(phone_number=phone_number))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            logger.debug(f"User not found for email: {email}, phone: {phone_number}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
