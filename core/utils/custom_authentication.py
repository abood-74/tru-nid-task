from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import APIKey
from django.utils import timezone
from django.db.models import Q

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            raise AuthenticationFailed('No API key provided')

        hashed_key = APIKey.hash_key(api_key)
        
        try:
            api_key_obj = APIKey.objects.select_related('user').get(
                Q(key_hash=hashed_key) &
                Q(is_active=True) &
                (Q(expires_at__gte=timezone.now()) | Q(expires_at__isnull=True))
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid or inactive API key')

        return (api_key_obj.user, api_key_obj)
