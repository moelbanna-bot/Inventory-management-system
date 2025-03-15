from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = 'products/products.html'
    paginate_by = 8
    context_object_name = 'products'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['current_page'] = self.request.GET.get('page', 1)
        context['latest_filter'] = self.request.GET.get('latest', False)
        return context

    def get_queryset(self):
        try:
            query_set = super().get_queryset()
            search_query = self.request.GET.get('search')
            latest_only = self.request.GET.get('latest')
            if search_query:
                query_set = query_set.filter(Q(name__iconatin=search_query) | Q(description__icontains=search_query))

            if latest_only:
                query_set = query_set.order_by('-created_at')

            return query_set
        except Exception as e:
            print(f"Error filtering products: {e}")
            return Product.objects.none()

# Create your views here.
