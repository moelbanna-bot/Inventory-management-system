from django.urls import path
from . import views

urlpatterns = [
    path("product/", views.AddProduct.as_view(), name="add_product"),
    path("product/<slug:slug>/", views.EditProduct.as_view(), name="edit_product"),
    path(
        "product/<slug:slug>/delete/",
        views.DeleteProduct.as_view(),
        name="delete_product",
    ),
]
