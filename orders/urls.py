from django.urls import path
from .views import OrderListView, OrderCreateView,SupermarketListView,AddSupermarketView,SupermarketDetailView

urlpatterns = [
    path("", OrderListView.as_view(), name="orders-list"),
    path("create/", OrderCreateView.as_view(), name="create_order"),
    path("list-supermarket/", SupermarketListView.as_view(), name="supermarkets-list"),
    path("supermarket/", AddSupermarketView.as_view(), name="add-supermarket"),
    path('supermarket/<int:id>/', SupermarketDetailView.as_view(), name='supermarket-detail'),
]
