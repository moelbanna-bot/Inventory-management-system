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
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.db.models import Count, Sum, F


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

        context["is_manager"] = self.request.user.is_staff

        if self.request.user.is_staff:
            context["low_stock_count"] = Product.objects.filter(
                current_quantity__lte=F("critical_quantity")
            ).count()

        last_6_months = []
        for i in range(5, -1, -1):
            date = datetime.now() - timedelta(days=30 * i)
            last_6_months.append(date.strftime("%b"))
        context["inventory_trends_labels"] = last_6_months

        inventory_data = []
        for i in range(5, -1, -1):
            date = datetime.now() - timedelta(days=30 * i)
            total = (
                Product.objects.filter(created_at__lte=date).aggregate(
                    total=Sum("current_quantity")
                )["total"]
                or 0
            )
            inventory_data.append(total)
        context["inventory_trends_data"] = inventory_data

        shipment_status = (
            Shipment.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        status_labels = []
        status_data = []
        for status in shipment_status:
            status_labels.append(status["status"])
            status_data.append(status["count"])

        context["shipment_status_labels"] = status_labels
        context["shipment_status_data"] = status_data

        monthly_shipments = (
            Shipment.objects.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")[:6]
        )

        monthly_labels = []
        monthly_data = []
        for shipment in monthly_shipments:
            monthly_labels.append(shipment["month"].strftime("%b"))
            monthly_data.append(shipment["count"])

        context["monthly_shipments_labels"] = monthly_labels
        context["monthly_shipments_data"] = monthly_data

        top_products = Product.objects.order_by("-current_quantity")[:5]
        top_products_labels = []
        top_products_data = []
        for product in top_products:
            top_products_labels.append(product.name)
            top_products_data.append(product.current_quantity)

        context["top_products_labels"] = top_products_labels
        context["top_products_data"] = top_products_data

        return context


class LowStockProductsView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "products/low_stock_products.html"
    context_object_name = "products"
    paginate_by = 8
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(
            current_quantity__lte=F("critical_quantity")
        ).order_by("current_quantity")
