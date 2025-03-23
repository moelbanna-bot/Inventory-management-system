from django.urls import path
from .views import OrderListView, create_order

urlpatterns = [
    path("", OrderListView.as_view(), name="orders-list"),
    path("create/", create_order, name="create_order"),
]
