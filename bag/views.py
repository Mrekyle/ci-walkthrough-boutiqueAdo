from django.shortcuts import render

# Create your views here.


def view_bag(request):
    """
    A view to render the back and its contents 
    """
    
    return render(request, 'bag.html')