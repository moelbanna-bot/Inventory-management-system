from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, CreateView, View,DetailView
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages

import json
from django.views import View
from django.db.models import Count
from .forms import SupermarketForm
from .models import Supermarket, Order
from django.db.models import Sum
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



class SupermarketListView(LoginRequiredMixin, ListView):
    model = Supermarket
    template_name = "orders/supermarkets.html"
    context_object_name = "supermarkets"
    ordering = ["name"]
    login_url = "login"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"] = self.request.GET.get("page", 1)
        context["form"] = SupermarketForm()
        return context

    def get_queryset(self):
        try:
            query_set = super().get_queryset().all()
            query_set = query_set.annotate(
                total_purchase_shipments=Count("order", distinct=True),
            )
            search_query = self.request.GET.get("search")

            if search_query:
                query_set = query_set.filter(
                    Q(name__icontains=search_query)
                    | Q(address__icontains=search_query)
                    | Q(email__icontains=search_query)
                )

            return query_set
        except Exception as e:
            print(f"Error filtering suppliers: {e}")
            return Supermarket.objects.none()


class AddSupermarketView(View):
    def post(self, request):
        form = SupermarketForm(request.POST)
        if form.is_valid():
            supermarket= form.save()
            messages.success(request, f"Supermarket '{supermarket.name}' added successfully!")
            return redirect("supermarkets-list")  # Adjust this to your actual URL name
        else:
            # Add show_modal flag to indicate we need to reopen the modal
            supermarkets = Supermarket.objects.all()
            return render(
                request,
                "orders/supermarkets.html",  # Adjust this to your actual template path
                {"supermarkets": supermarkets, "form": form, "show_modal": True},
            )



class SupermarketDetailView(LoginRequiredMixin, DetailView):
    model = Supermarket
    template_name = "orders/supermarket_details.html"
    context_object_name = "supermarket"
    login_url = "login"
    pk_url_kwarg = 'id'

    def get_queryset(self):
        query_set = super().get_queryset().filter(id=self.kwargs["id"])
        query_set = query_set.annotate(
            total_purchase_shipments=Count("order", distinct=True),
        )
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supermarket = self.object  # This is already set by DetailView


        orders = Order.objects.filter(supermarket=supermarket).order_by('-created_at')
        purchase_orders = []
        for order in orders:
            total_quantity = order.items.aggregate(total=Sum('quantity'))['total'] or 0
            status_display = order.get_status_display()
            purchase_orders.append({
                'id': order.reference_number,
                'due_date': order.access_date,
                'status': status_display,
                'item_count': total_quantity,
                'pk': order.pk
            })


        context['purchase_orders'] = purchase_orders
        context['type'] = 'supermarket'
        context['supermarket'].total_purchase_shipments = orders.count()

        if 'form' not in kwargs:
            context['form'] = SupermarketForm(instance=supermarket)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        supermarket = self.object

        if 'toggle_status' in request.POST:
            # Toggle is_active field
            supermarket.is_active = not supermarket.is_active
            supermarket.save()

            status = "activated" if supermarket.is_active else "deactivated"
            messages.success(request, f"Supermarket '{supermarket.name}' {status} successfully!")
        else:
            # This is a regular update request - use your existing logic
            form = SupermarketForm(request.POST, instance=supermarket)
            if form.is_valid():
                form.save()
                messages.success(request, f"Supermarket '{supermarket.name}' updated successfully!")
            else:
                context = self.get_context_data(form=form)
                return self.render_to_response(context)

        # Redirect back to the same page
        return redirect("supermarket-detail", id=supermarket.id)



