from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


def staff_or_moderator_required(view_func):
    """
    Access dey shudhu staff (is_staff=True) othoba 'Moderator' group-er
    user der. Baki shobai redirect/forbidden pabe.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        is_moderator = request.user.groups.filter(name='Moderator').exists()

        if request.user.is_staff or is_moderator:
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden("You don't have permission to access this page.")

    return wrapper
