from django.urls import path
from .views import (
    SupplierListView,
    AddSupplierView,
    SupplierDetailView,
    ShipmentListView,
    CreateShipmentView,
    ShipmentDetailView,
    ShipmentActionView,
)

urlpatterns = [
    path("", ShipmentListView.as_view(), name="shipment-list"),
    path("create/", CreateShipmentView.as_view(), name="create-shipment"),
    path("<str:ref_num>/", ShipmentDetailView.as_view(), name="shipment-detail"),
    path(
        "<str:ref_num>/action/<str:action>/",
        ShipmentActionView.as_view(),
        name="shipment-action",
    ),
    path("suppliers/", SupplierListView.as_view(), name="suppliers-list"),
    path("supplier/", AddSupplierView.as_view(), name="add-supplier"),
    path("supplier/<int:id>/", SupplierDetailView.as_view(), name="supplier-detail"),
]
