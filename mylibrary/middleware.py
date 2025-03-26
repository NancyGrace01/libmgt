from django.shortcuts import redirect
from django.conf import settings

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = ['/login/', '/signup/', '/admin/']
        if not request.user.is_authenticated and request.path not in allowed_paths:
            return redirect(settings.LOGIN_URL)

        librarian_only_paths = ['/admin/', '/add_book/', '/edit_book/', '/delete_book/']
        if request.path in librarian_only_paths and not request.user.is_staff:
            return redirect('/login/')
        
        return self.get_response(request)
