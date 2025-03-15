from django.shortcuts import render, redirect
from .forms import ProductForm
from .models import Product
from django.views import View
from django.contrib import messages


# Create your views here.
class AddProduct(View):
    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' added successfully!")
            return redirect("inventory")
        else:
            # Add show_modal flag to indicate we need to reopen the modal
            products = Product.objects.all()
            return render(
                request,
                "inventory.html",
                {"products": products, "form": form, "show_modal": True},
            )


class AllProducts(View):
    def get(self, request):
        search_query = request.GET.get("q", "")
        if search_query:
            products = Product.objects.filter(name__icontains=search_query)
        else:
            products = Product.objects.all()
        form = ProductForm()
        return render(request, "inventory.html", {"products": products, "form": form})


class EditProduct(View):
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            form = ProductForm(instance=product)
            return render(
                request,
                "inventory.html",
                {
                    "product": product,
                    "form": form,
                    "products": Product.objects.all(),
                    "show_modal": True,
                },
            )
        except Product.DoesNotExist:
            messages.error(request, "Product not found")
            return redirect("inventory")

    def post(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(
                    request, f"Product '{product.name}' updated successfully!"
                )
                return redirect("inventory")
            else:
                return render(
                    request,
                    "inventory.html",
                    {
                        "product": product,
                        "form": form,
                        "products": Product.objects.all(),
                        "show_modal": True,
                    },
                )
        except Product.DoesNotExist:
            messages.error(request, "Product not found")
            return redirect("inventory")
