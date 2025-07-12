import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, APIKey, APIUsage
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestAPIUsageLogging(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            tokens_balance=10
        )
        self.api_key, self.plain_key = APIKey.create_key(self.user, 'Test Key')
        self.url = reverse('national_ids:extract-egyptian-id')

    def test_api_usage_logged_on_success(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        initial_count = APIUsage.objects.count()
        
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert APIUsage.objects.count() == initial_count + 1
        
        usage = APIUsage.objects.latest('created_at')
        assert usage.api_key == self.api_key
        assert usage.tokens_used == 1
        assert usage.response_status == '200'
        assert usage.ip_address == '127.0.0.1'

    def test_api_usage_logged_on_validation_error(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        initial_count = APIUsage.objects.count()
        
        response = self.client.post(self.url, {
            'national_id': '123'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert APIUsage.objects.count() == initial_count + 1
        
        usage = APIUsage.objects.latest('created_at')
        assert usage.api_key == self.api_key
        assert usage.tokens_used == 0
        assert usage.response_status == '400'

    def test_api_usage_logged_on_insufficient_tokens(self):
        self.user.tokens_balance = 0
        self.user.save()
        
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        initial_count = APIUsage.objects.count()
        
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED
        assert APIUsage.objects.count() == initial_count + 1
        
        usage = APIUsage.objects.latest('created_at')
        assert usage.tokens_used == 0
        assert usage.response_status == '402'

    def test_api_usage_logs_correct_ip_from_x_forwarded_for(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(
            self.url,
            {'national_id': '29001010123456'},
            HTTP_X_FORWARDED_FOR='192.168.1.1, 10.0.0.1'
        )
        
        assert response.status_code == status.HTTP_200_OK
        usage = APIUsage.objects.latest('created_at')
        assert usage.ip_address == '192.168.1.1'

    def test_api_usage_logs_correct_ip_from_x_real_ip(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(
            self.url,
            {'national_id': '29001010123456'},
            HTTP_X_REAL_IP='192.168.1.2'
        )
        
        assert response.status_code == status.HTTP_200_OK
        usage = APIUsage.objects.latest('created_at')
        assert usage.ip_address == '192.168.1.2'

    def test_api_usage_logs_user_agent(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(
            self.url,
            {'national_id': '29001010123456'},
            HTTP_USER_AGENT='TestAgent/1.0'
        )
        
        assert response.status_code == status.HTTP_200_OK
        usage = APIUsage.objects.latest('created_at')
        assert usage.user_agent == 'TestAgent/1.0'

    def test_api_usage_graceful_failure(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        with patch('users.models.APIUsage.objects.create') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            response = self.client.post(self.url, {
                'national_id': '29001010123456'
            })
            
            assert response.status_code == status.HTTP_200_OK

    @patch('national_ids.views.logger')
    def test_api_usage_logs_creation_error(self, mock_logger):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        with patch('users.models.APIUsage.objects.create') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            response = self.client.post(self.url, {
                'national_id': '29001010123456'
            })
            
            assert response.status_code == status.HTTP_200_OK
            mock_logger.error.assert_called_once() 