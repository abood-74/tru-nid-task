import pytest
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed
from core.utils.custom_authentication import APIKeyAuthentication
from users.models import User, APIKey
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestAPIKeyAuthentication(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = APIKeyAuthentication()
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )

    def test_missing_api_key(self):
        request = self.factory.get('/')
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            self.auth.authenticate(request)
        
        assert 'No API key provided' in str(exc_info.value)

    def test_valid_api_key(self):
        api_key, plain_key = APIKey.create_key(self.user, 'Test Key')
        request = self.factory.get('/', HTTP_X_API_KEY=plain_key)
        
        user, auth_key = self.auth.authenticate(request)
        
        assert user == self.user
        assert auth_key == api_key

    def test_invalid_api_key(self):
        request = self.factory.get('/', HTTP_X_API_KEY='invalid_key')
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            self.auth.authenticate(request)
        
        assert 'Invalid or inactive API key' in str(exc_info.value)

    def test_inactive_api_key(self):
        api_key, plain_key = APIKey.create_key(self.user, 'Test Key', is_active=False)
        request = self.factory.get('/', HTTP_X_API_KEY=plain_key)
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            self.auth.authenticate(request)
        
        assert 'Invalid or inactive API key' in str(exc_info.value)

    def test_expired_api_key(self):
        past_time = timezone.now() - timedelta(days=1)
        api_key, plain_key = APIKey.create_key(self.user, 'Test Key', expires_at=past_time)
        request = self.factory.get('/', HTTP_X_API_KEY=plain_key)
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            self.auth.authenticate(request)
        
        assert 'Invalid or inactive API key' in str(exc_info.value)

    def test_valid_api_key_with_future_expiry(self):
        future_time = timezone.now() + timedelta(days=1)
        api_key, plain_key = APIKey.create_key(self.user, 'Test Key', expires_at=future_time)
        request = self.factory.get('/', HTTP_X_API_KEY=plain_key)
        
        user, auth_key = self.auth.authenticate(request)
        
        assert user == self.user
        assert auth_key == api_key 