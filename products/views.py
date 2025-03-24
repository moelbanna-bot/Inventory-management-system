from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product
from shipments.models import Shipment, Supplier
from .forms import ProductForm
from accounts.permissions import is_manager


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "products/products.html"
    paginate_by = 8
    context_object_name = "products"
    ordering = ["-created_at"]
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context["current_page"] = self.request.GET.get("page", 1)
        context["form"] = ProductForm()
        return context

    def get_queryset(self):
        try:
            query_set = super().get_queryset()
            search_query = self.request.GET.get("search")

            if search_query:
                query_set = query_set.filter(
                    Q(name__icontains=search_query)
                    | Q(description__icontains=search_query)
                )

            return query_set
        except Exception as e:
            print(f"Error filtering products: {e}")
            return Product.objects.none()


# Create your views here.
class AddProduct(LoginRequiredMixin, View):

    def post(self, request):
        if not is_manager(request.user):
            return self.handle_no_permission()

        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' added successfully!")

            return redirect("product-list")
        else:
            # Add show_modal flag to indicate we need to reopen the modal
            products = Product.objects.all()
            return render(
                request,
                "products/products.html",
                {"products": products, "form": form, "show_modal": True},
            )


class EditProduct(LoginRequiredMixin, View):
    def get(self, request, slug):
        if not is_manager(request.user):
            return self.handle_no_permission()
        try:
            product = Product.objects.get(slug=slug)
            form = ProductForm(instance=product)
            return render(
                request,
                "products/products.html",
                {
                    "product": product,
                    "form": form,
                    "products": Product.objects.all(),
                    "show_modal": True,
                },
            )
        except Product.DoesNotExist:
            messages.error(request, "Product not found")
            return redirect("product-list")

    def post(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(
                    request, f"Product '{product.name}' updated successfully!"
                )
                return redirect("product-list")

            else:
                return render(
                    request,
                    "products/products.html",
                    {
                        "product": product,
                        "form": form,
                        "products": Product.objects.all(),
                        "show_modal": True,
                    },
                )
        except Product.DoesNotExist:
            messages.error(request, "Product not found")
            return redirect("product-list")


class DeleteProduct(LoginRequiredMixin, View):
    def post(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            product_name = product.name
            product.delete()
            messages.success(request, f"Product '{product_name}' deleted successfully!")
            return redirect("product-list")
        except Product.DoesNotExist:
            messages.error(request, "Product not found")
            return redirect("product-list")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get top products with current_quantity (not stock)
        context["products"] = Product.objects.all().order_by("-current_quantity")[:5]

        # Get recent shipments
        context["recent_shipments"] = Shipment.objects.all().order_by("-created_at")[:5]

        # Get statistics
        context["total_products"] = Product.objects.count()
        context["total_shipments"] = Shipment.objects.count()
        context["total_suppliers"] = Supplier.objects.count()

        return context
