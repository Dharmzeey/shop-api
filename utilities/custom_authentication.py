from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed as e:
            # Check if the token has expired
            if 'Token is invalid or expired' in str(e) or 'Authorization header must contain two space-delimited values' in str(e):
                # Ignore expired tokens
                return None
            raise e