from django.shortcuts import render

# Create your views here.


def orders_list(request):
    return render(request, "orders/orders.html")
