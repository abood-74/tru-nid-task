import pytest
from django.test import TestCase
from users.models import User, APIKey, APIUsage
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestUserModel(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        assert user.email == 'test@example.com'
        assert user.tokens_balance == 0
        assert user.is_active is True

    def test_add_tokens(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        new_balance = user.add_tokens(100)
        assert new_balance == 100
        assert user.tokens_balance == 100

    def test_deduct_tokens_sufficient_balance(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            tokens_balance=100
        )
        result = user.deduct_tokens(50)
        assert result is True
        assert user.tokens_balance == 50

    def test_deduct_tokens_insufficient_balance(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            tokens_balance=10
        )
        result = user.deduct_tokens(50)
        assert result is False
        assert user.tokens_balance == 10

    def test_has_sufficient_tokens(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            tokens_balance=100
        )
        assert user.has_sufficient_tokens(50) is True
        assert user.has_sufficient_tokens(150) is False


@pytest.mark.django_db
class TestAPIKeyModel(TestCase):

    def test_create_api_key(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        api_key, plain_key = APIKey.create_key(user, 'Test Key')
        
        assert api_key.user == user
        assert api_key.name == 'Test Key'
        assert api_key.is_active is True
        assert plain_key.startswith('nid_')

    def test_key_hashing(self):
        plain_key = 'test_key'
        hashed_key = APIKey.hash_key(plain_key)
        assert hashed_key != plain_key
        assert len(hashed_key) == 64

    def test_is_expired_no_expiry(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        api_key, _ = APIKey.create_key(user, 'Test Key')
        assert api_key.is_expired() is False

    def test_is_expired_with_future_expiry(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        future_time = timezone.now() + timedelta(days=1)
        api_key, _ = APIKey.create_key(user, 'Test Key', expires_at=future_time)
        assert api_key.is_expired() is False

    def test_is_expired_with_past_expiry(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        past_time = timezone.now() - timedelta(days=1)
        api_key, _ = APIKey.create_key(user, 'Test Key', expires_at=past_time)
        assert api_key.is_expired() is True

    def test_is_valid_active_key(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        api_key, _ = APIKey.create_key(user, 'Test Key')
        assert api_key.is_valid() is True

    def test_is_valid_inactive_key(self):
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        api_key, _ = APIKey.create_key(user, 'Test Key', is_active=False)
        assert api_key.is_valid() is False 