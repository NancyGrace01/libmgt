from django.shortcuts import redirect
from django.conf import settings

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        allowed_paths = ['/login/', '/signup/']
        if (not request.user.is_authenticated and 
            not path.startswith('/admin/') and 
            path not in allowed_paths):
            return redirect(settings.LOGIN_URL)

        librarian_only_paths = ['/add_book/', '/edit_book/', '/delete_book/']
        if any(path.startswith(p) for p in librarian_only_paths) and not request.user.is_staff:
            return redirect('/login/')

        return self.get_response(request)