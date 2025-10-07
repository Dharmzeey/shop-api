import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)

class OptionalJWTAuthentication(JWTAuthentication):
    """
    Try to authenticate with SimpleJWT. If there's no token or token is invalid,
    *do not raise* — just return None so request proceeds as anonymous.
    """
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            # validate token and return (user, validated_token) on success
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except (InvalidToken, TokenError, AuthenticationFailed) as exc:
            # Log for debugging but don't block the request
            logger.debug("OptionalJWTAuthentication: token invalid or expired: %s", exc)
            return None
        except Exception as exc:
            # Unexpected errors — log them. Optionally return None to avoid 401.
            logger.exception("OptionalJWTAuthentication unexpected error: %s", exc)
            return None
