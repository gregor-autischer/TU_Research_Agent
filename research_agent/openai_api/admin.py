from django.contrib import admin as django_admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from research_agent.admin import admin_site
from .models import UserProfile, Conversation, Message, Paper, Verification, PaperVerification


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


class MessageInline(django_admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)


class ConversationAdmin(django_admin.ModelAdmin):
    list_display = ('title', 'user', 'message_count', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


class PaperAdmin(django_admin.ModelAdmin):
    list_display = ('title_short', 'authors', 'date', 'user', 'in_context', 'created_at')
    list_filter = ('user', 'in_context', 'paper_type', 'created_at')
    search_fields = ('title', 'authors', 'summary')
    readonly_fields = ('created_at',)
    list_editable = ('in_context',)

    def title_short(self, obj):
        return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
    title_short.short_description = 'Title'


class PaperVerificationInline(django_admin.TabularInline):
    model = PaperVerification
    extra = 0
    readonly_fields = ('paper_index', 'title', 'credibility_score', 'overall_quality', 'created_at')
    fields = ('paper_index', 'title', 'credibility_score', 'overall_quality', 'created_at')
    can_delete = False


class VerificationAdmin(django_admin.ModelAdmin):
    list_display = ('message', 'confidence_score', 'paper_count', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('message', 'confidence_score', 'textual_verification', 'summary', 'created_at')
    inlines = [PaperVerificationInline]
    
    def paper_count(self, obj):
        return obj.paper_verification_details.count()
    paper_count.short_description = 'Papers'


# Register with custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(UserProfile, UserProfileAdmin)
admin_site.register(Conversation, ConversationAdmin)
admin_site.register(Paper, PaperAdmin)
admin_site.register(Verification, VerificationAdmin)
