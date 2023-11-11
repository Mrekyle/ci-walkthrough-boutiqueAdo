from django.shortcuts import render, get_object_or_404

from .models import UserProfile

# Create your views here.


def profile(request):
    """
        Renders the profile page
    """

    profile = get_object_or_404(UserProfile, user=request.user)

    template = 'profiles.html'
    context = {
        'profile': profile,
    }

    return render(request, template, context)
