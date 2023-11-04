from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    # Giving the order number to the web address as the argument for the success page
    path('checkout/<order_number>',
         views.checkout_success, name='checkout_success'),
]
