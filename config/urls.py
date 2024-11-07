# Import necessary modules and functions from Django and DRF (Django REST Framework)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

admin.site.site_url = None

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('', include('apps.attandance.urls')),
]


# If needed, add static file serving settings in development (not recommended for production)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)