from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.contrib import messages
from .forms import SupplierForm, ShipmentForm
from .models import Supplier, Shipment, ShipmentItem
from django.shortcuts import get_object_or_404
from django.db import transaction
from products.models import Product
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
    pk_url_kwarg = "id"

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
        shipments = Shipment.objects.filter(supplier=supplier).order_by("-created_at")

        # For each shipment, we'll get the total quantity of all products
        purchase_orders = []
        for shipment in shipments:
            # Calculate the total quantity across all shipment items
            # This sums up the quantity field from all shipment items
            total_quantity = (
                shipment.items.aggregate(total=Sum("quantity"))["total"] or 0
            )

            # Get the status display name
            status_display = shipment.get_status_display()

            # Add formatted shipment data to the list
            purchase_orders.append(
                {
                    "id": shipment.reference_number,
                    "due_date": shipment.access_date,
                    "status": status_display,
                    "item_count": total_quantity,
                    "pk": shipment.pk,
                }
            )

        # Add purchase orders to context
        context["purchase_orders"] = purchase_orders

        # Add the type to differentiate between supplier and supermarket
        context["type"] = "supplier"

        # Calculate total purchase shipments for the supplier
        context["supplier"].total_purchase_shipments = shipments.count()

        # Add form for updating supplier
        if "form" not in kwargs:
            context["form"] = SupplierForm(instance=supplier)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        supplier = self.object

        # Check if this is a toggle is_active request
        if "toggle_status" in request.POST:
            # Toggle is_active field
            supplier.is_active = not supplier.is_active
            supplier.save()

            status = "activated" if supplier.is_active else "deactivated"
            messages.success(
                request, f"Supplier '{supplier.name}' {status} successfully!"
            )
        else:
            # This is a regular update request - use your existing logic
            form = SupplierForm(request.POST, instance=supplier)
            if form.is_valid():
                form.save()
                messages.success(
                    request, f"Supplier '{supplier.name}' updated successfully!"
                )
            else:
                # If the form is invalid, re-render the page with the form errors
                context = self.get_context_data(form=form)
                return self.render_to_response(context)

        # Redirect back to the same page
        return redirect("supplier-detail", id=supplier.id)


class CreateShipmentView(LoginRequiredMixin, TemplateView):
    template_name = "shipments/create_shipment.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["suppliers"] = Supplier.objects.filter(is_active=True)
        context["products"] = Product.objects.all()
        context["form"] = ShipmentForm()
        return context

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            supplier_id = data.get("supplier")
            products = data.getlist("product[]")
            quantities = data.getlist("quantity[]")
            access_date = data.get("access_date")

            if not supplier_id or not products or not quantities or not access_date:
                messages.error(request, "Please provide all required information")
                return redirect("create-shipment")

            supplier = Supplier.objects.get(id=supplier_id)

            # Create shipment with generated reference number
            shipment = Shipment.objects.create(
                supplier=supplier,
                status="PN",
                created_by=request.user,
                access_date=access_date,
            )

            for product_id, quantity in zip(products, quantities):
                product = Product.objects.get(id=product_id)
                ShipmentItem.objects.create(
                    shipment=shipment, product=product, quantity=quantity
                )

            messages.success(
                request, f"Shipment #{shipment.reference_number} created successfully!"
            )
            return redirect("shipment-list")

        except Exception as e:
            messages.error(request, f"Error creating shipment: {str(e)}")
            return redirect("create-shipment")


class ShipmentListView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = "shipments/shipments.html"
    context_object_name = "shipments"
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
                | Q(supplier__name__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related("supplier", "created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"] = self.request.GET.get("page", 1)
        context["status_choices"] = Shipment.STATUS_SHIPMENT_CHOICES
        return context


class ShipmentDetailView(LoginRequiredMixin, DetailView):
    model = Shipment
    template_name = "shipments/shipment_detail.html"
    context_object_name = "shipment"
    login_url = "login"
    slug_field = "reference_number"
    slug_url_kwarg = "ref_num"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipment = self.object
        
        context["can_confirm"] = shipment.status == Shipment.PENDING
        context["can_ship"] = shipment.status == Shipment.CONFIRMED
        context["can_deliver"] = shipment.status == Shipment.SHIPPED
        # Only show cancel option if user is staff and shipment status is pending or confirmed
        context["can_cancel"] = self.request.user.is_staff and shipment.status in [
            Shipment.PENDING,
            Shipment.CONFIRMED,
        ]
        return context


class ShipmentActionView(LoginRequiredMixin, View):
    def post(self, request, ref_num, action):
        shipment = get_object_or_404(Shipment, reference_number=ref_num)

        try:
            if action == "confirm" and shipment.status == Shipment.PENDING:
                if not request.user.is_staff:
                    messages.error(request, "Only staff members can confirm shipments.")
                    return redirect(
                        "shipment-detail", ref_num=shipment.reference_number
                    )
                shipment.mark_as_confirmed(request.user)
                messages.success(
                    request,
                    f"Shipment #{shipment.reference_number} has been confirmed.",
                )
            elif action == "ship" and shipment.status == Shipment.CONFIRMED:
                shipment.mark_as_shipped()
                messages.success(
                    request,
                    f"Shipment #{shipment.reference_number} has been marked as shipped.",
                )
            elif action == "deliver" and shipment.status == Shipment.SHIPPED:
                with transaction.atomic():
                    for item in shipment.items.all():
                        product = item.product
                        product.current_quantity += item.quantity
                        product.save()

                    shipment.mark_as_delivered()
                    messages.success(
                        request,
                        f"Shipment #{shipment.reference_number} has been marked as delivered and inventory updated.",
                    )
            elif action == "cancel" and shipment.status in [
                Shipment.PENDING,
                Shipment.CONFIRMED,
            ]:
                # Check if user is staff
                if not request.user.is_staff:
                    messages.error(request, "Only staff members can cancel shipments.")
                    return redirect(
                        "shipment-detail", ref_num=shipment.reference_number
                    )
                shipment.mark_as_cancelled()
                messages.success(
                    request,
                    f"Shipment #{shipment.reference_number} has been cancelled.",
                )
            else:
                messages.error(request, "Invalid action for current shipment status.")
        except Exception as e:
            messages.error(request, f"Error updating shipment: {str(e)}")

        return redirect("shipment-detail", ref_num=shipment.reference_number)
