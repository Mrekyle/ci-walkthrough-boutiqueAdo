from django.shortcuts import render, redirect, reverse,  get_object_or_404
from django.contrib import messages
# Generating a search query using the Q model
from django.db.models import Q
from .models import Product, Category
from django.db.models.functions import Lower
from products.forms import ProductForm

# Requires the user to be logged into the application to view the url
from django.contrib.auth.decorators import login_required

# Create your views here.


def all_products(request):
    """
    View to return and render the all products on the app,
    allows the user to sort and search.

    By first defining the query and category as none it ensures
    that we have an empty search field to start with. Meaning no bugs or confusion will occur
    with the search or category selections

    Using the '__' is common in django search and filtering and general query's by drilling into a related model
    This allows us to search for the related names of certain items in the models. If they are related by foreign keys
    """

    product = Product.objects.all()
    query = None
    category = None
    sort = None
    direction = None

    if request.GET:
        """
        Checking if the GET request contains certain parameters such as the product category or
        the 'q' from the submitted search form or is there is a sort request.
        """

        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                product = product.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            product = product.order_by(sortkey)

        if 'category' in request.GET:
            """
            By splitting the string into a list at the ',' we are then able to use that list as
            as the filter parameters for the category
            """
            category = request.GET['category'].split(',')
            product = product.filter(category__name__in=category)
            category = Category.objects.filter(name__in=category)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!")
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
            queries = Q(name__icontains=query) | Q(
                description__icontains=query)
            product = product.filter(queries)

    current_sorting = f'{sort}_{direction}'

    """
    The context is allowing us to pass data through to the website front end of the website under certain
    names.

    Such as the current_categories context will allow us to display what current category has been selected
    as a search parameter by the user on the front end of the website
    """
    context = {
        'products': product,
        'search_term': query,
        'current_categories': category,
        'current_sorting': current_sorting,
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


@login_required
def add_product(request):
    """
        Renders the product management page for the staff of the application
    """

    """
        Checking if the store owner/admin is logged in. And if not. 
        Then redirecting the user back to the home page, as they dont have access
        to view that page
    """

    if not request.user.is_superuser:
        messages.error(request, f'Sorry, you dont have access to this page. \
                       Only store owners can do that!')
        return redirect(reverse('home'))

    """
        Handling the form being submitted and catching the information

        Catching the information by using request.post and catching the files
        by using the request.files method
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product successfully added")
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, f"Oops, something went wrong. Please check for errors and try again. \
                           If the problem persists, please contact support for further assistance.")
    else:
        # Form to be used on the template
        form = ProductForm()

    # Template of the view
    template = 'add_product.html'

    # Context of the view
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """
        Renders the edit a product view
    """

    if not request.user.is_superuser:
        messages.error(request, f'Sorry, you dont have access to this page. \
                       Only store owners can do that!')
        return redirect(reverse('home'))

    # Getting the products previous information
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        # Ensuring that the instance of the product form is the current one selected
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Successfully edited product: {product.name}')
            # Returning the user to the newly edited product page
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, f'Oops, somethings gone wrong. Please check for errors and try again. \
                            Or contact support for further assistance.')
    else:
        # Filling the form with the products current information
        form = ProductForm(instance=product)
        # Alerting the user of the product they are currently editing
        messages.info(request, f'You are currently editing {product.name}')

    template = 'edit_product.html'

    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """
        Deletes a product. When that certain url and product id has
        been accessed in the url.
    """

    if not request.user.is_superuser:
        messages.error(request, f'Sorry, you dont have access to this page. \
                       Only store owners can do that!')
        return redirect(reverse('home'))

    # Getting the product using the products id
    product = get_object_or_404(Product, pk=product_id)
    # Deleting the product with the delete method
    product.delete()
    messages.success(request, f'{product.name} has been deleted successfully.')

    return redirect(reverse('products'))
