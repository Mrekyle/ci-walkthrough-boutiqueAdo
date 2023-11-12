from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from . models import UserProfile
from . forms import UserProfileForm
from checkout.models import Order

# Create your views here.


@login_required
def profile(request):
    """
        Renders the profile page
    """

    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, (f'Information updated successfully!'))
        else:
            messages.error(request, (f'Information update failed. Please try again or \
                           contact us for further support'))
    else:
        # Getting the users order history and returning all of the previous orders
        orders = profile.orders.all()

    # Populating the form with the users information set from making a purchase
    form = UserProfileForm(instance=profile)

    template = 'profiles.html'
    context = {
        'form': form,
        'orders': orders,
        # Allows us to avoid displaying certain information when on the profile page
        'on_profile_page': True,
    }

    return render(request, template, context)


@login_required
def order_history(request, order_number):
    """
        Rendering the order history of the users order. When the user
        clicks on a specific order they will be shown the order confirmation page.

        This allows us to not have to build a separate page to show the same order information.

        Again by using a boolean value in the context, we can check where the user is coming from
        and render something specific for that instance
    """

    order = get_object_or_404(Order, order_number=order_number)

    messages.info(
        request, (f'This is a past confirmation for a previous order. '
                  'A confirmation email was sent of the date the order was placed.'))

    template = 'checkout/checkout_success.html'

    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)
