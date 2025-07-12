from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
import secrets
import hashlib
import hmac
from typing import Tuple
from django.utils import timezone

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    tokens_balance = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return self.email
    
    def add_tokens(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Cannot add negative tokens")
        self.tokens_balance += amount
        self.save(update_fields=['tokens_balance'])
        return self.tokens_balance
    
    def deduct_tokens(self, amount: int) -> bool:
        if amount < 0:
            raise ValueError("Cannot deduct negative tokens")
        if self.tokens_balance >= amount:
            self.tokens_balance -= amount
            self.save(update_fields=['tokens_balance'])
            return True
        return False
    
    def has_sufficient_tokens(self, amount: int) -> bool:
        return self.tokens_balance >= amount
    

class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key_hash = models.CharField(max_length=128, unique=True) 
    name = models.CharField(max_length=100)  
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.name}"
    
    
    @classmethod
    def generate_key(cls) -> str:
        return f"nid_{secrets.token_urlsafe(32)}"
    
    @classmethod
    def hash_key(cls, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
    
    @classmethod
    def create_key(cls, user: User, name: str, **kwargs) -> Tuple['APIKey', str]:
        plain_key = cls.generate_key()
        hashed_key = cls.hash_key(plain_key)
        
        api_key = cls.objects.create(
            user=user,
            key_hash=hashed_key,
            name=name,
            **kwargs
        )
        return api_key, plain_key
    
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired()

class APIUsage(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    tokens_used = models.IntegerField(default=1)
    response_status = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['api_key']),
            models.Index(fields=['created_at'])
        ]