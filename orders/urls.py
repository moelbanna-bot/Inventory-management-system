from django.urls import path

from .views import (
    OrdersListView,
    CreateOrderView,
    SupermarketListView,
    AddSupermarketView,
    SupermarketDetailView,
)

app_name = "orders"
urlpatterns = [
    path("", OrdersListView.as_view(), name="orders-list"),
    path("create/", CreateOrderView.as_view(), name="create-order"),
    path("list-supermarket/", SupermarketListView.as_view(), name="supermarkets-list"),
    path("supermarket/", AddSupermarketView.as_view(), name="add-supermarket"),
    path(
        "supermarket/<int:id>/",
        SupermarketDetailView.as_view(),
        name="supermarket-detail",
    ),
]
