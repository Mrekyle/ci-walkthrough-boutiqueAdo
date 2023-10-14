from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

"""
By using the separate context file this allows us to use all the context from this file
in every template across the application without having to retrieve the data from different
urls and other requests. Ensuring we add it to the site wide contexts in settings.py
"""

def bag_contents(request):
    
    bag_items = []
    total = 0
    product_count = 0

#   Getting the products from the session in the bag variable 
    bag = request.session.get('bag', {})

    for item_id, quantity in bag.items():
         product = get_object_or_404(Product, pk=item_id)

     #     Multiplying the count by the price of the product 
         total += quantity * product.price

     #     Adding the product count of items in the bag to the quantity variable
         product_count += quantity

     #     Adding items to the context for use in the bag template view 
         bag_items.append({
              'item_id': item_id,
              'quantity': quantity,
              'product': product,
         })

    if total < settings.FREE_DELIVERY_THRESHOLD:
         delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE)
         free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
         delivery = 0
         free_delivery_delta = 0

    grand_total = delivery + total

    context = {
         'bag_items':  bag_items,
         'total': total,
         'product_count': product_count,
         'delivery': delivery,
         'free_delivery_delta': free_delivery_delta,
         'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
         'grand_total': grand_total,
    }

    return context  