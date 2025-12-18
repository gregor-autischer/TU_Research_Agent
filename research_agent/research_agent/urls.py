from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/', include('openai_api.urls')),
    path('', include('web_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
