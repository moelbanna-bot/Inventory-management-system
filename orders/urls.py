from django.urls import path

from .views import (
    OrdersListView,
    SupermarketListView,
    AddSupermarketView,
    SupermarketDetailView,
)

app_name = "orders"
urlpatterns = [
    path("", OrdersListView.as_view(), name="orders-list"),
    path("list-supermarket/", SupermarketListView.as_view(), name="supermarkets-list"),
    path("supermarket/", AddSupermarketView.as_view(), name="add-supermarket"),
    path(
        "supermarket/<int:id>/",
        SupermarketDetailView.as_view(),
        name="supermarket-detail",
    ),
]
