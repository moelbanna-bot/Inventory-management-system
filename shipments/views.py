from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from .models import Supplier, Shipment


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = "shipments/suppliers.html"
    context_object_name = "suppliers"
    ordering = ["name"]
    login_url = "login"
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"] = self.request.GET.get("page", 1)
        return context

    def get_queryset(self):
        try:
            query_set = super().get_queryset().filter(is_active=True)
            query_set = query_set.annotate(
                total_purchase_shipments=Count("shipment", distinct=True),
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
            return Supplier.objects.none()
