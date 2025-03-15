from django.urls import path
from . import views

urlpatterns = [
    path("product/", views.AddProduct.as_view(), name="add_product"),
    path("products/", views.AllProducts.as_view(), name="inventory"),
    path("product/<slug:slug>/", views.EditProduct.as_view(), name="edit_product"),
]
