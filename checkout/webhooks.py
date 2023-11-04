from django.conf import settings
from django.http import HttpResponse

# Makes the view require the POST request and reject any other request's
from django.views.decorators.http import require_POST

# As stripe doesn't send the csrf token. We need to ensure that it is exempt. So the forms will still be submitted
from django.views.decorators.csrf import csrf_exempt


from checkout.webhook_handler import StripeWH_Handler
import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """
        Listens for the webhooks from stripes API
    """

    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api.key = settings.STRIPE_SECRET_KEY

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e,)

    """
        STRIPE CODE  
        
        If a certain event happens, then call 
        the specific function to handle it 
        
        if event.type == 'payment_intent.succeeded':
            payment_intend = event.data.object
            print('PaymentIntent was Successful!')
        elif event.type == 'payment_method.attached':
            payment_method = event.data.object
            print('PaymentMethod was attached to a Customer!')
        else:
            return HttpResponse(status=400)

        return HttpResponse(status=200)
    """
