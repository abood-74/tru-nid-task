from django.contrib import admin
from users.models import User, APIKey

# Register your models here.
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_active', 'created_at', 'expires_at')
    readonly_fields = ('created_at', 'updated_at', 'key_hash')
    fields = ('user', 'name', 'is_active', 'expires_at', 'created_at', 'updated_at', 'key_hash')

    def save_model(self, request, obj, form, change):
        if not change:
            api_key, plain_key = APIKey.create_key(user=obj.user, name=obj.name, expires_at=obj.expires_at)
            obj.key_hash = api_key.key_hash
            self.message_user(request, f"API Key generated: {plain_key}")
        else:
            super().save_model(request, obj, form, change)

admin.site.register(APIKey, APIKeyAdmin)
admin.site.register(User)
