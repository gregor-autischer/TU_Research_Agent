from django.contrib import admin as django_admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from research_agent.admin import admin_site
from .models import UserProfile


class UserProfileInline(django_admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'has_api_key')

    def has_api_key(self, obj):
        return bool(obj.profile.openai_api_key) if hasattr(obj, 'profile') else False
    has_api_key.boolean = True
    has_api_key.short_description = 'API Key Set'


class UserProfileAdmin(django_admin.ModelAdmin):
    list_display = ('user', 'has_api_key', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def has_api_key(self, obj):
        return bool(obj.openai_api_key)
    has_api_key.boolean = True
    has_api_key.short_description = 'API Key Set'


# Register with custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(UserProfile, UserProfileAdmin)
