from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView, View, TemplateView
from django.views.generic import ListView, CreateView, View, DetailView
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
                    Q(reference_number__icontains=search_query)
                    | Q(supermarket__name__icontains=search_query)
                    | Q(supermarket__email__icontains=search_query)
                )

            return query_set
        except Exception as e:
            print(f"Error filtering Orders: {e}")
            return Order.objects.none()


class CreateOrderView(View):
    def post(self, request, *args, **kwargs):
        supermarket_id = request.POST.get("supermarket_id")
        if not supermarket_id:
            messages.error(request, "Please select a supermarket.")
            return redirect("orders:orders-list")

        supermarket = Supermarket.objects.get(id=supermarket_id)
        with transaction.atomic():
            order = Order.objects.create(
                supermarket=supermarket,
                created_by=request.user,
                access_date=timezone.now(),
            )
            request.session["order_id"] = order.id
            return redirect(reverse("orders:add_order", kwargs={"pk": order.id}))


class AddOrderView(TemplateView):
    template_name = "orders/add-order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, id=self.kwargs["pk"])
        context["order"] = order
        context["order_items"] = order.items.all()
        context["products"] = Product.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs["pk"])
        product_id = request.POST.get("product")
        quantity = request.POST.get("quantity")

        if product_id and quantity:
            product = get_object_or_404(Product, id=product_id)
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            messages.success(request, "Product added successfully.")
        else:
            messages.error(request, "Please select a product and quantity.")

        return redirect(reverse("orders:add_order", kwargs={"pk": order.id}))


class PlaceOrderView(View):
    def post(self, request, *args, **kwargs):
        order_id = request.session.get("order_id")
        if not order_id:
            messages.error(request, "No order found.")
            return redirect("orders:orders-list")

        order = get_object_or_404(Order, id=order_id)
        if order.items.count() == 0:
            order.delete()
            messages.error(request, "Order cancelled as no items were added.")
            return redirect("orders:orders-list")
        order.save()
        messages.success(request, "Order placed successfully.")
        return redirect("orders:orders-list")


@require_POST
def cancel_order(request):
    order_id = request.session.get("order_id")
    if not order_id:
        messages.error(request, "No order found.")
        return redirect("orders:orders-list")

    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, "Order cancelled successfully.")
    return redirect("orders:orders-list")


from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect


@require_POST
def delete_order_item(request, pk):
    order_item = get_object_or_404(OrderItem, pk=pk)
    order_id = order_item.order.id
    order_item.delete()
    messages.success(request, "Order item deleted successfully.")
    return HttpResponseRedirect(reverse("orders:add_order", kwargs={"pk": order_id}))


class EditOrderItemView(View):
    def post(self, request, pk, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, pk=pk)
        quantity = request.POST.get("quantity")

        if quantity:
            order_item.quantity = quantity
            order_item.save()
            messages.success(request, "Order item updated successfully.")
        else:
            messages.error(request, "Please enter a valid quantity.")

        return HttpResponseRedirect(
            reverse("orders:add_order", kwargs={"pk": order_item.order.id})
        )


class OrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = "orders/add-order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(
            Order, reference_number=self.kwargs["reference_number"]
        )
        context["order"] = order
        context["order_items"] = order.items.all()
        return context


class OrderStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_reference_number = self.kwargs["reference_number"]
        order = get_object_or_404(Order, reference_number=order_reference_number)

        if "confirm" in request.POST:
            order.mark_as_confirmed(request.user)
            messages.success(request, "Order confirmed successfully.")
        elif "update" in request.POST:
            new_status = request.POST.get("order_status_dropdown")
            print("##### newStatus#####", new_status)
            if new_status in ["confirmed", "shipped", "delivered", "cancelled"]:
                order.status = new_status
                order.save()
                messages.success(request, f"Order status updated to {new_status}.")
            else:
                messages.error(request, "Invalid status selected.")

        return redirect("orders:order_details", reference_number=order_reference_number)


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
                total_purchase_orders=Count("order", distinct=True),
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
            supermarket = form.save()
            messages.success(request, f"Supermarket '{supermarket.name}' added successfully!")
            return redirect("orders:supermarkets-list")  # Adjust this to your actual URL name
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
            total_purchase_orders=Count("order", distinct=True),
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
        return redirect("orders:supermarket-detail", id=supermarket.id)
