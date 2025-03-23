from django.urls import path
from .views import OrderListView, OrderCreateView

urlpatterns = [
    path("", OrderListView.as_view(), name="orders-list"),
    path("create/", OrderCreateView.as_view(), name="create_order"),
]
