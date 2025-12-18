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

    # Chat endpoint
    path('chat/', views.chat, name='chat'),
]
