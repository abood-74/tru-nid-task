import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, APIKey
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from core.utils.custom_throttles import EgyptianIDThrottle


@pytest.mark.django_db
class TestEgyptianIDThrottle(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            tokens_balance=100
        )
        self.api_key, self.plain_key = APIKey.create_key(self.user, 'Test Key')
        self.url = reverse('national_ids:extract-egyptian-id')
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_throttle_class_is_configured(self):
        from national_ids.views import EgyptianIDExtractorAPIView
        view = EgyptianIDExtractorAPIView()
        assert EgyptianIDThrottle in view.throttle_classes

    def test_throttle_has_correct_rate(self):
        throttle = EgyptianIDThrottle()
        assert throttle.rate == '1000/hour'

    def test_throttle_allows_requests_within_limit(self):
        with patch.object(EgyptianIDThrottle, 'rate', '3/hour'):
            throttle = EgyptianIDThrottle()
            throttle.rate = '3/hour'
            
            self.client.credentials(HTTP_X_API_KEY=self.plain_key)
            
            for i in range(3):
                response = self.client.post(self.url, {
                    'national_id': '29001010123456'
                })
                assert response.status_code == status.HTTP_200_OK

    def test_throttle_per_user_basis(self):
        user2 = User.objects.create_user(
            email='test2@example.com',
            first_name='Test2',
            last_name='User2',
            tokens_balance=100
        )
        api_key2, plain_key2 = APIKey.create_key(user2, 'Test Key 2')
        
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        assert response.status_code == status.HTTP_200_OK
        
        self.client.credentials(HTTP_X_API_KEY=plain_key2)
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        assert response.status_code == status.HTTP_200_OK

    def test_throttle_doesnt_affect_unauthenticated_requests(self):
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_throttle_inherits_from_user_rate_throttle(self):
        from rest_framework.throttling import UserRateThrottle
        assert issubclass(EgyptianIDThrottle, UserRateThrottle)

    def test_throttle_blocks_requests_with_low_rate(self):
        with patch.object(EgyptianIDThrottle, 'allow_request', return_value=False):
            with patch.object(EgyptianIDThrottle, 'wait', return_value=3600):
                self.client.credentials(HTTP_X_API_KEY=self.plain_key)
                
                response = self.client.post(self.url, {
                    'national_id': '29001010123456'
                })
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_throttle_adds_retry_after_header(self):
        with patch.object(EgyptianIDThrottle, 'allow_request', return_value=False):
            with patch.object(EgyptianIDThrottle, 'wait', return_value=3600):
                self.client.credentials(HTTP_X_API_KEY=self.plain_key)
                
                response = self.client.post(self.url, {
                    'national_id': '29001010123456'
                })
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                assert 'Retry-After' in response 