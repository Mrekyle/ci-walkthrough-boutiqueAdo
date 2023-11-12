"""
    IMPORTS
"""
# Django email imports - Required to send emails
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from django.http import HttpResponse
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import stripe
import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """
            Send the user a confirmation email of there order
        """

        # Getting the users email address to send the confirmation too
        cust_email = order.email

        # Rendering the confirmation subject and body txt files to a string.
        # With the first being the file to return as a string and second giving
        # the information we want to pass to the email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order},
        )

        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL},
        )
        # Sending the email to the user. Passing all the different information we wish to send to the user.
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            # Email address of the user to send the email too
            [cust_email],
        )

    def handle_event(self, event):
        """
            Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        # Getting the details from the payment intent for use to create an order in the database
        billing_details = stripe_charge.billing_details  # updated
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)  # updated

        # Clean data inside of the shipping details
        for field, value in shipping_details.address_items():
            if value == "":
                shipping_details.address[field] = None

        profile = None
        username = intent.metadata.username

        # Checking if the user is authenticated by comparing the values of the username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)

            # If the user is authenticated then use the users default shipping information as the shipping information
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        order_exists = False
        """
            Setting an attempt variable and a while loop to create a delay in creating the order in the database. 
            This allows the stripe API to have time to do everything it needs to do on the back end
        """
        attempt = 1

        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.name,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    stripe_pid=pid,
                    original_bag=bag,
                )
                order_exists = True
                break
            except Order.DoesNotExist:

                # Iterating through the loop to the count of 5
                attempt += 1

                # Sleeping the code to allow everything to catch up on itself.
                time.sleep(1)

            """
                If there is an order in the database. Then return the 200 status response
                
                Else try find the order. 
            """
            if order_exists:
                # Sending the confirmation email to the user once it has been saved to the database
                self._send_confirmation_email(order)
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: Verified order exists in the database.',
                    status=200)
            else:
                order = None
                try:
                    order = Order.objects.create(
                        full_name=shipping_details.name,
                        user_profile=profile,
                        email=billing_details.name,
                        phone_number=shipping_details.phone,
                        country=shipping_details.address.country,
                        postcode=shipping_details.address.postal_code,
                        town_or_city=shipping_details.address.city,
                        street_address1=shipping_details.address.line1,
                        street_address2=shipping_details.address.line2,
                        county=shipping_details.address.state,
                        stripe_pid=pid,
                        original_bag=bag
                    )
                    for item_id, item_data in json.loads(bag).items():
                        product = Product.objects.get(id=item_id)
                        if isinstance(item_data, int):
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=item_data,
                            )
                            order_line_item.save()
                        else:
                            for size, quantity in item_data['items_by_size'].items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=size,
                                )
                                order_line_item.save()
                except Exception as e:
                    if order:
                        Order.delete()
                    return HttpResponse(
                        content=f'Webhook received: {event["type"]} | ERROR: {e}', status=500
                    )
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Order created in Stripe Webhook.',
                status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
