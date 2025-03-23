from django.urls import path
from .views import SupplierListView


urlpatterns = [
    path("", SupplierListView.as_view(), name="suppliers-list"),
]
