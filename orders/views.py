from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView

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


def create_order(request):
    return render(request, "orders/add-order.html")
