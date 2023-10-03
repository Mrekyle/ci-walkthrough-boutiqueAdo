from django.shortcuts import render, redirect

# Create your views here.


def view_bag(request):
    """
    A view to render the back and its contents 
    """
    
    return render(request, 'bag.html')

def add_to_bag(request, item_id):
    """
    Adds the selected quantity of the specified item to the shopping bag
    """

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')

    """
    By using the http storage it allows us to store users items in a bag
    during the session of the user. This allows the user to go and select
    multiple items from across the store to purchase
    """
    bag = request.session.get('bag', {})

    """
    If the item already exists in the bag, add to the the quantity of the item
    else, add the item to the bag
    """
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        bag[item_id] = quantity

    request.session['bag'] = bag
    return redirect(redirect_url)