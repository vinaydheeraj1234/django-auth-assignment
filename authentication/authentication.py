from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token


class CookieTokenAuthentication(SessionAuthentication):
    def authenticate(self, request):
        self.enforce_csrf(request)

        token_key = request.COOKIES.get("auth_token")
        if not token_key:
            return None

        try:
            token = Token.objects.select_related("user").get(key=token_key)
        except Token.DoesNotExist:
            return None

        if not token.user.is_active:
            return None

        return (token.user, token)