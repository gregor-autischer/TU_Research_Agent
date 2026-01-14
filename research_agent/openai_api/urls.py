from django.urls import path
from . import views
from . import auth_views
from . import views_verification

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

    # Project endpoints
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),

    # Conversation endpoints
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('conversations/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('conversations/<int:pk>/chat/', views.conversation_chat, name='conversation_chat'),

    # Paper endpoints
    path('papers/', views.paper_list, name='paper_list'),
    path('papers/<int:pk>/', views.paper_detail, name='paper_detail'),
    path('papers/<int:pk>/generate-bibtex/', views.paper_generate_bibtex, name='paper_generate_bibtex'),
    path('papers/<int:pk>/copy/', views.copy_paper_to_project, name='copy_paper_to_project'),

    # Verification endpoints
    path('messages/<int:message_id>/verify/', views_verification.verify_message, name='verify_message'),
]
