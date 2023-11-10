from django.shortcuts import render

# Create your views here.


def profile(request):
    """
        Renders the profile page
    """

    template = 'profiles.html'
    context = {}

    return render(request, template, context)
