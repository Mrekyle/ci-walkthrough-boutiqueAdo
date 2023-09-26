from django.shortcuts import render

# Create your views here.


def index(request):
    """
    View to return and render the index page of the home
    app
    """
    
    return render(request, 'home/index.html')