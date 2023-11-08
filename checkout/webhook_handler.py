# from django.http import HttpResponse


# class StripeWH_Handler:
#     """
#         Handle the stripe webhooks
#     """

#     # Saving the request incase it is required for later use
#     def __init__(self, request):
#         self.request = request

#     def handle_event(self, event):
#         """
#             Handles a generic/unknown/unexpected webhook event
#         """

#         # If the response of a webhook was received it will tell
#         return HttpResponse(
#             content=f'Unhandled Webhook received: {event["type"]}',
#             status=200)

#     def handle_payment_intent_succeeded(self, event):
#         """
#             Handle the payment_intent.succeeded webhook from stripe
#         """

#         # Payment intents data
#         intent = event.data.object
#         print(intent)

#         return HttpResponse(
#             content=f'Successful Payment Webhook received: {event["type"]}',
#             status=200
#         )

#     def handle_payment_intent_payment_failed(self, event):
#         """
#             Handle the payment_intent.payment_failed webhook from stripe
#         """

#         return HttpResponse(
#             content=f'Failed Payment Webhook received: {event["type"]}',
#             status=200
#         )

from django.http import HttpResponse

import stripe
import json


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

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

        order_exists = False
        try:
            order = Order.objects.get(
                full_name__iexact=shipping_details.name,
                email__iexact=shipping_details.name,
                phone_number__iexact=shipping_details.phone,
                country__iexact=shipping_details.country,
                postcode__iexact=shipping_details.postal_code,
                town_or_city__iexact=shipping_details.city,
                street_address1__iexact=shipping_details.line1,
                street_address2__iexact=shipping_details.line2,
                county__iexact=shipping_details.state,
                grand_total=grand_total,
            )

            order_exists = True
            return HttpResponse(
                content=f'Webhook received: {event["type"] | SUCCESS: Verified order exists in the database.}',
                status=200)
        except Order.DoesNotExist:
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=shipping_details.name,
                    phone_number=shipping_details.phone,
                    country=shipping_details.country,
                    postcode=shipping_details.postal_code,
                    town_or_city=shipping_details.city,
                    street_address1=shipping_details.line1,
                    street_address2=shipping_details.line2,
                    county=shipping_details.state,
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

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
