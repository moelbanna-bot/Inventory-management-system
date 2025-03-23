from django.urls import path
from .views import SupplierListView, AddSupplierView, SupplierDetailView

urlpatterns = [
    path("", SupplierListView.as_view(), name="suppliers-list"),
    path("supplier/", AddSupplierView.as_view(), name="add-supplier"),
    path('supplier/<int:id>/', SupplierDetailView.as_view(), name='supplier-detail'),

]
