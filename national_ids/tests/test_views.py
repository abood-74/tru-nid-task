import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, APIKey
from unittest.mock import patch


@pytest.mark.django_db
class TestEgyptianIDExtractorAPIView(TestCase):

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

    def test_successful_id_extraction(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['success'] is True
        assert data['data']['national_id'] == '29001010123456'
        assert data['data']['governorate'] == 'Cairo'
        assert data['data']['gender'] == 'male'

    def test_invalid_id_format(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(self.url, {
            'national_id': '123'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_api_key(self):
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_api_key(self):
        self.client.credentials(HTTP_X_API_KEY='invalid_key')
        
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_insufficient_tokens(self):
        self.user.tokens_balance = 0
        self.user.save()
        
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED
        data = response.json()
        assert data['success'] is False

    def test_tokens_deducted_on_success(self):
        initial_balance = self.user.tokens_balance
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(self.url, {
            'national_id': '29001010123456'
        })
        
        self.user.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert self.user.tokens_balance == initial_balance - 1

    def test_tokens_not_deducted_on_error(self):
        initial_balance = self.user.tokens_balance
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(self.url, {
            'national_id': '123'
        })
        
        self.user.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.user.tokens_balance == initial_balance

    def test_missing_national_id_field(self):
        self.client.credentials(HTTP_X_API_KEY=self.plain_key)
        
        response = self.client.post(self.url, {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST 