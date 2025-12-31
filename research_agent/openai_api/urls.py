from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    # Auth endpoints
    path('auth/csrf/', auth_views.get_csrf_token, name='csrf'),
    path('auth/register/', auth_views.register_view, name='register'),
    path('auth/login/', auth_views.login_view, name='login'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
    path('auth/user/', auth_views.get_user, name='get_user'),
    path('auth/api-key/', auth_views.save_api_key, name='save_api_key'),
    path('auth/api-key/delete/', auth_views.delete_api_key, name='delete_api_key'),

    # Chat endpoint (legacy, kept for backwards compatibility)
    path('chat/', views.chat, name='chat'),

    # Conversation endpoints
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('conversations/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('conversations/<int:pk>/chat/', views.conversation_chat, name='conversation_chat'),

    # Paper endpoints
    path('papers/', views.paper_list, name='paper_list'),
    path('papers/<int:pk>/', views.paper_detail, name='paper_detail'),
    path('papers/<int:pk>/generate-bibtex/', views.paper_generate_bibtex, name='paper_generate_bibtex'),

    # Verification endpoints
    path('messages/<int:message_id>/verify/', views.verify_message, name='verify_message'),
]
