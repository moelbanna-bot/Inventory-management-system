from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, CreateView, View
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
import json

from orders.models import Order, Supermarket, OrderItem
from products.models import Product


class OrderListView(ListView):
    model = Order
    template_name = "orders/orders.html"
    paginate_by = 8
    context_object_name = "orders"
    ordering = ["-created_at"]
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["supermarkets"] = Supermarket.objects.all()
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
            print(f"Error filtering Orders: {e}")
            return Order.objects.none()


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = "orders/add-order.html"

    def get(self, request, *args, **kwargs):
        # Redirect to orders list if accessed directly without POST
        return redirect("orders-list")

    def post(self, request, *args, **kwargs):
        # Check if this is a form submission to create an order
        if "submit_order" in request.POST:
            try:
                # Get data from form
                supermarket_id = request.POST.get("supermarket_id")
                products_json = request.POST.get("products_json")

                if not products_json or not supermarket_id:
                    messages.error(request, "Missing required data")
                    return redirect("orders-list")

                # Parse products JSON
                products_data = json.loads(products_json)
                print("****products_data*****", products_data)

                if not products_data:
                    messages.error(request, "No products selected")
                    return redirect("orders-list")

                # Create the order
                supermarket = Supermarket.objects.get(id=supermarket_id)
                order = Order.objects.create(
                    supermarket=supermarket,
                    access_date=timezone.now().date(),
                    created_by=request.user,
                )

                # Create order items
                for product_data in products_data:
                    OrderItem.objects.create(
                        order=order,
                        product_id=product_data["productId"],
                        quantity=product_data["quantity"],
                    )

                messages.success(
                    request, f"Order #{order.reference_number} created successfully"
                )
                return redirect("orders-list")

            except Exception as e:
                print(f"Error creating order: {e}")
                messages.error(request, f"Failed to create order: {e}")
                return redirect("orders-list")

        # If this is initial supermarket selection to show order form
        supermarket_id = request.POST.get("supermarket")
        if supermarket_id:
            try:
                supermarket = Supermarket.objects.get(id=supermarket_id)
                products = Product.objects.all()

                context = {
                    "supermarket": supermarket,
                    "temp_ref_number": "Not assigned yet",
                    "order_date": timezone.now(),
                    "status": "New",
                    "products": products,
                }
                return render(request, self.template_name, context)

            except Supermarket.DoesNotExist:
                messages.error(request, "Supermarket not found")
                return redirect("orders-list")

        return redirect("orders-list")
