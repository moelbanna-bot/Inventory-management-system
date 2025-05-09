from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.views import View
from django.db.models import Count
from .forms import SupermarketForm, OrderForm
from django.db.models import Sum
from orders.models import Order, Supermarket, OrderItem
from products.models import Product


# order views
class OrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/orders.html"
    context_object_name = "orders"
    ordering = ["-created_at"]
    login_url = "login"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        status_filter = self.request.GET.get("status")

        if search_query:
            queryset = queryset.filter(
                Q(reference_number__icontains=search_query)
                | Q(supermarket__name__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related("supermarket", "created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"] = self.request.GET.get("page", 1)
        context["status_choices"] = Order.STATUS_ORDER_CHOICES
        return context


class CreateOrderView(LoginRequiredMixin, TemplateView):
    template_name = "orders/create_order.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["supermarkets"] = Supermarket.objects.filter(is_active=True)
        context["products"] = Product.objects.all()
        context["form"] = OrderForm()
        return context

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            supermarket_id = data.get("supermarket")
            products = data.getlist("product[]")
            quantities = data.getlist("quantity[]")
            access_date = data.get("access_date")

            if not supermarket_id or not products or not quantities or not access_date:
                messages.error(request, "Please provide all required information")
                return redirect("orders:create-order")

            supermarket = Supermarket.objects.get(id=supermarket_id)

            # Create order with generated reference number
            order = Order.objects.create(
                supermarket=supermarket,
                status="PN",
                created_by=request.user,
                access_date=access_date,
            )

            for product_id, quantity in zip(products, quantities):
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order, product=product, quantity=quantity
                )
            with transaction.atomic():
                for item in order.items.all():
                    product = item.product
                    if product.current_quantity < item.quantity:
                        messages.error(
                            request,
                            f"Insufficient stock for product {product.name}, it has only {product.current_quantity} available.",
                        )
                        order.delete()
                        return redirect("orders:create-order")
                    product.current_quantity -= item.quantity
                    product.save()

            messages.success(
                request, f"Order #{order.reference_number} created successfully!"
            )
            return redirect("orders:orders-list")

        except Exception as e:
            messages.error(request, f"Error creating order: {str(e)}")
            return redirect("orders:create-order")


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_details.html"
    context_object_name = "order"
    login_url = "login"
    slug_field = "reference_number"
    slug_url_kwarg = "ref_num"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        context["can_confirm"] = order.status == Order.PENDING
        context["can_ship"] = order.status == Order.CONFIRMED
        context["can_deliver"] = order.status == Order.SHIPPED
        # Only show cancel option if user is staff and order status is pending or confirmed
        context["can_cancel"] = self.request.user.is_staff and order.status in [
            Order.PENDING,
            Order.CONFIRMED,
        ]
        return context


class OrderActionView(LoginRequiredMixin, View):
    def post(self, request, ref_num, action):
        order = get_object_or_404(Order, reference_number=ref_num)

        try:
            if action == "confirm" and order.status == Order.PENDING:
                if not request.user.is_staff:
                    messages.error(request, "Only staff members can confirm orders.")
                    return redirect("order-details", ref_num=order.reference_number)
                order.mark_as_confirmed(request.user)
                messages.success(
                    request,
                    f"Order #{order.reference_number} has been confirmed.",
                )
            elif action == "ship" and order.status == Order.CONFIRMED:
                order.mark_as_shipped()
                messages.success(
                    request,
                    f"Order #{order.reference_number} has been marked as shipped.",
                )
            elif action == "deliver" and order.status == Order.SHIPPED:
                order.mark_as_delivered()
                messages.success(
                    request,
                    f"Order #{order.reference_number} has been marked as delivered.",
                )
            elif action == "cancel" and order.status in [
                Order.PENDING,
                Order.CONFIRMED,
            ]:
                if not request.user.is_staff:
                    messages.error(request, "Only staff members can cancel orders.")
                    return redirect("order-details", ref_num=order.reference_number)

                with transaction.atomic():
                    for item in order.items.all():
                        product = item.product
                        product.current_quantity += item.quantity
                        product.save()

                order.mark_as_cancelled()
                messages.success(
                    request,
                    f"Order #{order.reference_number} has been cancelled.",
                )
            else:
                messages.error(request, "Invalid action for current order status.")
        except Exception as e:
            messages.error(request, f"Error updating order: {str(e)}")

        return redirect("orders:order-details", ref_num=order.reference_number)


# supermarket views
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


class AddSupermarketView(LoginRequiredMixin, View):
    def post(self, request):
        form = SupermarketForm(request.POST)
        if form.is_valid():
            supermarket = form.save()
            messages.success(
                request, f"Supermarket '{supermarket.name}' added successfully!"
            )
            return redirect(
                "orders:supermarkets-list"
            )  # Adjust this to your actual URL name

            messages.success(
                request, f"Supermarket '{supermarket.name}' added successfully!"
            )
            return redirect(
                "orders:supermarkets-list"
            )  # Adjust this to your actual URL name

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
    pk_url_kwarg = "id"

    def get_queryset(self):
        query_set = super().get_queryset().filter(id=self.kwargs["id"])
        query_set = query_set.annotate(
            total_purchase_orders=Count("order", distinct=True),
        )
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supermarket = self.object  # This is already set by DetailView

        orders = Order.objects.filter(supermarket=supermarket).order_by("-created_at")
        purchase_orders = []
        for order in orders:
            total_quantity = order.items.aggregate(total=Sum("quantity"))["total"] or 0
            status_display = order.get_status_display()
            purchase_orders.append(
                {
                    "id": order.reference_number,
                    "due_date": order.access_date,
                    "status": status_display,
                    "item_count": total_quantity,
                    "pk": order.pk,
                }
            )

        context["purchase_orders"] = purchase_orders
        context["type"] = "supermarket"
        context["supermarket"].total_purchase_shipments = orders.count()

        if "form" not in kwargs:
            context["form"] = SupermarketForm(instance=supermarket)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        supermarket = self.object

        if "toggle_status" in request.POST:
            # Toggle is_active field
            supermarket.is_active = not supermarket.is_active
            supermarket.save()

            status = "activated" if supermarket.is_active else "deactivated"
            messages.success(
                request, f"Supermarket '{supermarket.name}' {status} successfully!"
            )
        else:
            # This is a regular update request - use your existing logic
            form = SupermarketForm(request.POST, instance=supermarket)
            if form.is_valid():
                form.save()
                messages.success(
                    request, f"Supermarket '{supermarket.name}' updated successfully!"
                )
            else:
                context = self.get_context_data(form=form)
                return self.render_to_response(context)

        # Redirect back to the same page
        return redirect("orders:supermarket-detail", id=supermarket.id)
