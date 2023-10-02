from django.shortcuts import render
from .models import Product

# Create your views here.


def all_products(request):
    """
    View to return and render the all products on the app,
    allows the user to sort and search
    """
    
    product = Product.objects.all()

    context = {
        'products': product
    }

    return render(request, 'products.html', context)