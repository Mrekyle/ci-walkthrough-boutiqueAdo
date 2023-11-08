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
        print(intent)
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
