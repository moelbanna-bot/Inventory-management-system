from django.urls import path
from .views import (
    OrderListView,
    CreateOrderView,
    AddOrderView,
    PlaceOrderView,
    cancel_order,
    delete_order_item,
    EditOrderItemView,
    OrderDetailView,
)

app_name = "orders"
urlpatterns = [
    path("", OrderListView.as_view(), name="orders-list"),
    path("create-order/", CreateOrderView.as_view(), name="create_order"),
    path("add-order/<int:pk>/", AddOrderView.as_view(), name="add_order"),
    path("place-order/", PlaceOrderView.as_view(), name="place_order"),
    path("cancel-order/", cancel_order, name="cancel_order"),
    path(
        "delete-order-item/<int:pk>/",
        delete_order_item,
        name="delete_order_item",
    ),
    path(
        "edit-order-item/<int:pk>/", EditOrderItemView.as_view(), name="edit_order_item"
    ),
    path(
        "order-detail/<str:reference_number>/",
        OrderDetailView.as_view(),
        name="order_details",
    ),
]
