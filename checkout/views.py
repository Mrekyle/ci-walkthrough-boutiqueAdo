from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
# Importing the logic for the total amount of the shopping cart into this file to allow us to use that logic
from bag.contexts import bag_contents

from .models import Order, OrderLineItem

# Importing the products model
from products.models import Product

import stripe

# Create your views here.


def checkout(request):

    # Setting a variable of the stripe keys for use inside of the view
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    """
        Handling the post method of the checkout form. Allowing
        the user to be redirected back to another page if there is an error.
        Creating the order in the database and resetting the checkout bag
    """
    if request == 'POST':
        bag = request.session.get('bag', {})

        # Getting all the form data submitted by the user
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # Inputting the retrieved form data into a new instance of the order form
        order_form = OrderForm(form_data)

        # Checking to see if the order form is valid before saving and submitting to the database
        if order_form.is_valid():
            order = order_form.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    # If the item doesn't have a size variable
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        # If the item does have a size variable
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                        order_line_item.save()
                # If the product doesn't exist. Then the error message will be returned. and the user redirected
                except Product.DoesNotExist:
                    messages.error(request, (
                        'One of the products in your bag was not found in our database.'
                        'Please get in touch with us for further assistance!'
                    ))
                    order.delete()
                    return redirect(reverse('view_bag'))

            # If the user wants to save the information to there account data
            request.session['save-info'] = 'save-info' in request.POST

            # Redirecting the user once the checkout has been completed
            return redirect(reverse('checkout_success'), args=[order.order_number])
    else:
        # If there is an error in any of the code above/with the basket/checkout process an error message is displayed
        messages.error(
            request, 'There is an error with your shopping bag. \
                Please contact us for further assistance!')

        """
            Getting the items from inside of the bag to allow the calculation
            of the grand_total and for payment methods to be submitted 
        """
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(
                request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        # Calling the function to be run
        current_bag = bag_contents(request)

        # Getting the grand total value of the shopping bag for use inside of the view of the cart
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
        # Checking if the intent was correctly created by stripe
        print(intent)

        # The order form created in the forms.py file using crispy forms. And then given to the context of the view
        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(
            request, 'Stripe public key is missing. Please contact the Admin team to get this fixed.')

    template = 'checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handles the successful checkouts
    Redirecting the user back to another page
    Giving a success message to the user
    And deleting the current bag from the session after
    a successful checkout
    """

    # If the user opted to save the information for future purchases
    save_info = request.session.get('save-info')

    # Getting the order from the session for use in success messages.
    # By setting the order_number we can use it without prefixing with 'order....'
    order = get_object_or_404(Order, order_number=order_number)

    messages.success(request, f'Order succesfully processed. \
                     Your order number is {order_number}. \
                        An email confirmation will be sent to {order.email} shortly.')

    # Deleting the users bag from the session once the checkout was successful
    if 'bag' in request.session:
        del request.session['bag']
    else:
        messages.info(request, 'There are no items in your shopping bag. \
                      Please have a browse around.')

    # Setting the template to be used and giving the context of items for use inside of the template
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,

    }

    # Rendering the template with the context included
    return render(request, template, context)
