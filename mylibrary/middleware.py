from django.shortcuts import redirect
from django.conf import settings


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        user = request.user

        allowed_paths = [
            '/login/', '/signup/', '/admin-login/', '/verify_email/', '/admin-register/'
        ]

        if not user.is_authenticated and path not in allowed_paths:
            return redirect(settings.LOGIN_URL)

        admin_only_paths = [
            '/add_book/', '/edit_book/', '/delete_book/', '/admin-dashboard/',
        ]

        if any(path.startswith(p) for p in admin_only_paths):
            if not user.is_authenticated:
                return redirect('/admin-login/')
            
            if not hasattr(user, 'role') or user.role not in ['librarian', 'receptionist']:
                return redirect('/login/')

        if path == '/book-list/':
            if user.is_authenticated and hasattr(user, 'role') and user.role in ['librarian', 'receptionist']:
                return redirect('/admin-dashboard/')

        return self.get_response(request)


class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = ['/signup/', '/login/', '/verify_email/', '/logout/', '/admin/', '/admin-dashboard/']

        if request.user.is_authenticated:
            user = request.user
            if hasattr(user, 'role') and user.role in ['librarian', 'receptionist']:
                return self.get_response(request)
            if hasattr(user, 'profile') and not user.profile.email_verified:
                if not any(request.path.startswith(p) for p in allowed_paths):
                    return redirect('verify_email')
        
        return self.get_response(request)



