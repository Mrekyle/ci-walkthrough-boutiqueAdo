from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from .forms import OrderForm

# Create your views here.


def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    order_form = OrderForm()
    template = 'checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51O3xR7HkfpmhxD3hoRtHTWXd5nkIiUss1qbiYcM5qYiKaZs4b2UjfQzbskcqvy0UkS7yTwAzlKuJMWMQLGET5SMp002vPnkcyP',
        'client_secret': 'Hello World',
    }

    return render(request, template, context)
