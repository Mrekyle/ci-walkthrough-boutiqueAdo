from django.shortcuts import render, redirect, reverse,  get_object_or_404
from django.contrib import messages 
# Generating a search query using the Q model 
from django.db.models import Q
from .models import Product

# Create your views here.


def all_products(request):
    """
    View to return and render the all products on the app,
    allows the user to sort and search
    """ 
    
    product = Product.objects.all()
    query = None

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            """
            The 'i' in front of the contains method ensures that the query isn't case sensitive
            Meaning it will return the same object no matter what the user or the database data
            says as long as it finds the match.

            The 'Q' Essentially means to search through the database for matching parameters that
            were entered by the user in the search bar. Searching for matching data in the name and
            description.

            The '|' is the or operator. Meaning this or that... 
            """
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            product = product.filter(queries)

    context = {
        'products': product,
        'search_term': query,
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