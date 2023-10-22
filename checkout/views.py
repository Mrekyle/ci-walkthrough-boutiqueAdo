from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
# Importing the logic for the total amount of the shopping cart into this file to allow us to use that logic
from bag.contexts import bag_contents

import stripe

# Create your views here.


def checkout(request):

    # Setting a variable of the stripe keys for use inside of the view
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
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
