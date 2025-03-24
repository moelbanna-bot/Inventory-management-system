from django.urls import path

from .views import (
    OrdersListView,
    CreateOrderView,
    OrderDetailView,
    SupermarketListView,
    AddSupermarketView,
    SupermarketDetailView,
    OrderActionView,
)

app_name = "orders"
urlpatterns = [
    path("", OrdersListView.as_view(), name="orders-list"),
    path("create/", CreateOrderView.as_view(), name="create-order"),
    path("<str:ref_num>/", OrderDetailView.as_view(), name="order-details"),
    path(
        "<str:ref_num>/action/<str:action>/",
        OrderActionView.as_view(),
        name="order-action",
    ),
    path("list-supermarket/", SupermarketListView.as_view(), name="supermarkets-list"),
    path("supermarket/", AddSupermarketView.as_view(), name="add-supermarket"),
    path(
        "supermarket/<int:id>/",
        SupermarketDetailView.as_view(),
        name="supermarket-detail",
    ),
]
