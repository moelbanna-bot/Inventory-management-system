from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.contrib import messages
from .forms import SupplierForm
from .models import Supplier, Shipment
from django.db.models import Sum


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
            query_set = super().get_queryset().all()
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


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = "shipments/supplier_details.html"
    context_object_name = "supplier"
    login_url = "login"
    pk_url_kwarg = 'id'

    def get_queryset(self):
        query_set = super().get_queryset().filter(id=self.kwargs["id"])
        query_set = query_set.annotate(
            total_purchase_shipments=Count("shipment", distinct=True),
        )
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.object  # This is already set by DetailView

        # Get all shipments for this supplier, ordered by creation date (newest first)
        shipments = Shipment.objects.filter(supplier=supplier).order_by('-created_at')

        # For each shipment, we'll get the total quantity of all products
        purchase_orders = []
        for shipment in shipments:
            # Calculate the total quantity across all shipment items
            # This sums up the quantity field from all shipment items
            total_quantity = shipment.items.aggregate(total=Sum('quantity'))['total'] or 0

            # Get the status display name
            status_display = shipment.get_status_display()

            # Add formatted shipment data to the list
            purchase_orders.append({
                'id': shipment.reference_number,
                'due_date': shipment.access_date,
                'status': status_display,
                'item_count': total_quantity,
                'pk': shipment.pk
            })

        # Add purchase orders to context
        context['purchase_orders'] = purchase_orders

        # Add the type to differentiate between supplier and supermarket
        context['type'] = 'supplier'

        # Calculate total purchase shipments for the supplier
        context['supplier'].total_purchase_shipments = shipments.count()

        # Add form for updating supplier
        if 'form' not in kwargs:
            context['form'] = SupplierForm(instance=supplier)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        supplier = self.object

        # Check if this is a toggle is_active request
        if 'toggle_status' in request.POST:
            # Toggle is_active field
            supplier.is_active = not supplier.is_active
            supplier.save()

            status = "activated" if supplier.is_active else "deactivated"
            messages.success(request, f"Supplier '{supplier.name}' {status} successfully!")
        else:
            # This is a regular update request - use your existing logic
            form = SupplierForm(request.POST, instance=supplier)
            if form.is_valid():
                form.save()
                messages.success(request, f"Supplier '{supplier.name}' updated successfully!")
            else:
                # If the form is invalid, re-render the page with the form errors
                context = self.get_context_data(form=form)
                return self.render_to_response(context)

        # Redirect back to the same page
        return redirect("supplier-detail", id=supplier.id)
