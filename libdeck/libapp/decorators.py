from django.shortcuts import redirect
from functools import wraps

def student_login(view_func):
    """
    Decorator to ensure a user is logged in via Google.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            if request.session['user_data']:
                return view_func(request, *args, **kwargs)
        except:
            return redirect('sign_in')

    return _wrapped_view
