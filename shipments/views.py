from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.contrib import messages
from .forms import SupplierForm
from .models import Supplier


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = "shipments/suppliers.html"
    context_object_name = "suppliers"
    ordering = ["name"]
    login_url = "login"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"] = self.request.GET.get("page", 1)
        context["form"] = SupplierForm()
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


class AddSupplierView(View):
    def post(self, request):
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"Supplier '{supplier.name}' added successfully!")
            return redirect("suppliers-list")  # Adjust this to your actual URL name
        else:
            # Add show_modal flag to indicate we need to reopen the modal
            suppliers = Supplier.objects.all()
            return render(
                request,
                "shipments/suppliers.html",  # Adjust this to your actual template path
                {"suppliers": suppliers, "form": form, "show_modal": True},
            )
