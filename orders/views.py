from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import ListView, CreateView

from orders.models import Order, Supermarket


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

    def post(self, request, *args, **kwargs):
        supermarket_id = request.POST.get("supermarket")

        if supermarket_id:
            try:

                supermarket = Supermarket.objects.get(id=supermarket_id)

                context = {
                    "supermarket": supermarket,
                    "temp_ref_number": "Not assigned yet",
                    "order_date": timezone.now(),
                    "status": "Draft",
                }
                return render(request, self.template_name, context)

            except Supermarket.DoesNotExist:
                return redirect("orders-list")

        return redirect("orders-list")

    def get(self, request, *args, **kwargs):
        return redirect("orders")
