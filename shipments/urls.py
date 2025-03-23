from django.urls import path
from .views import SupplierListView, AddSupplierView

urlpatterns = [
    path("", SupplierListView.as_view(), name="suppliers-list"),
    path("supplier/", AddSupplierView.as_view(), name="add-supplier"),
]
