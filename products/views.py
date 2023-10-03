from django.shortcuts import render, get_object_or_404
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


def product_detail(request, product_id):
    """
    View each product individually on its own page
    Passing the individual primary key of the product to the url 
    Allowing the rendering of that products details on the page
    """
    
    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product
    }

    return render(request, 'product_detail.html', context)