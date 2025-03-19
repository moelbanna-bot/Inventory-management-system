from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ProductListView

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
]
