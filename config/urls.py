"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import DashboardView
from django.http import HttpResponse, JsonResponse
import os
import sys
from django.views.static import serve
from django.urls import re_path

# Simple health check view
def health_check(request):
    db_config = {
        'database_url_set': 'DATABASE_URL' in os.environ,
        'django_settings': os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set'),
        'python_version': sys.version,
        'working_directory': os.getcwd(),
    }
    return JsonResponse({'status': 'ok', 'config': db_config})

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("admin/johncena/rko", admin.site.urls),
    path("products/", include("products.urls")),
    path("accounts/", include("accounts.urls")),
    path("orders/", include("orders.urls")),
    path("shipments/", include("shipments.urls")),
    path("health/", health_check, name="health_check"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]