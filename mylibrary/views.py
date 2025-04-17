import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages
from .models import Book, BorrowedBook, Profile, Category, CustomUser, AdminProfile
from django.contrib.auth.models import User
from datetime import timedelta, date
from django.http import JsonResponse, HttpResponseForbidden
from django.core.mail import send_mail, EmailMessage
from django.utils import timezone
from django.contrib.auth import login, logout
from datetime import timedelta
from .forms import BookForm, CategoryForm, ProfileForm
from django.db.models import Q
from functools import wraps


def home(request):
    return render(request, 'book_list.html')  

#ADMIN
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                user_role = getattr(request.user, 'role', None)
                if user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "You do not have permission to view this page.")
                    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))
            else:
                messages.warning(request, "Please log in to access this page.")
                return redirect('login')
        return _wrapped_view
    return decorator

@login_required
@role_required(['librarian', 'receptionist'])
def admin_dashboard(request):
    
    total_books = Book.objects.count()
    total_users = Profile.objects.count()
    borrowed_books = BorrowedBook.objects.filter(status='Borrowed').count()
    
    try:
        profile = AdminProfile.objects.get(user=request.user)
        admin_name = profile.user.username
        role = profile.user.role
        profile_pic = profile.user.profile_picture.url if hasattr(profile.user, 'profile_picture') and profile.user.profile_picture else '/static/images/default.jpg'
    except AdminProfile.DoesNotExist:
        admin_name = request.user.username
        role = 'Admin'
        profile_pic = '/static/images/default.jpg'

    context = {
        'total_books': total_books,
        'total_users': total_users,
        'borrowed_books': borrowed_books,
        'admin_name': admin_name,
        'profile_pic': profile_pic,
        'role': role,
    }
    
    return render(request, 'admin_dashboard.html', context)


def admin_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not username or not email or not password or not role:
            messages.error(request, "All fields are required.")
            return redirect('admin_register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('admin_register')

        user = CustomUser.objects.create_user(username=username, email=email, password=password, role=role)
        user.save()
        messages.success(request, "Registration successful. You can now log in.")
        return redirect('admin_login')

    return render(request, 'register.html')


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user and (user.role == 'librarian' or user.role == 'receptionist'):
            auth_login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or access denied.')

    return render(request, 'admin_login.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@login_required
@role_required(['librarian', 'receptionist'])
def borrowed_books(request):
    borrowed_books = BorrowedBook.objects.select_related('borrower', 'book').all()
    context = {
        'borrowed_books': borrowed_books
    }
    return render(request, 'borrowed_books.html', context)

@login_required
def books(request):
    books = Book.objects.all()
    return render(request, 'books.html', {'books': books})


@login_required
def add_book(request):
    if request.user.role not in ['librarian']:
        return HttpResponseForbidden("Access denied: Only Librarians can add books.")

    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('books')
    else:
        form = BookForm()

    return render(request, 'add_book.html', {'form': form})

@role_required(['librarian'])
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, f"Book '{book.title}' has been deleted.")
    return redirect('books')

@role_required(['librarian'])
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        category_id = request.POST.get('category')

        if category_id:
            book.category = get_object_or_404(Category, id=category_id)

        book.save()
        messages.success(request, "Book updated successfully.")
        return redirect('books')

    return render(request, 'edit_book.html', {
        'book': book,
        'categories': categories
    })

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "category_list.html", {'categories': categories})

@role_required(['librarian'])
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

@role_required(['librarian'])
def cat_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
    return redirect('category_list')

@login_required
def users_list(request):
    query = request.GET.get('q')
    gender_filter = request.GET.get('gender')
    state_filter = request.GET.get('state')

    users = Profile.objects.select_related('user').all()

    if query:
        users = users.filter(
            Q(full_name__icontains=query) |
            Q(city__icontains=query) |
            Q(occupation__icontains=query)
        )

    if gender_filter:
        users = users.filter(gender=gender_filter)

    if state_filter:
        users = users.filter(state=state_filter)

    return render(request, 'users_list.html', {
        'users': users,
        'query': query,
        'gender_filter': gender_filter,
        'state_filter': state_filter,
    })
    
    
@login_required
@role_required(['librarian'])
def edit_user(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users_list')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_user.html', {'form': form, 'profile': profile})


@login_required
@role_required(['librarian'])
def delete_user(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    profile.user.delete()
    return redirect('users_list')


#USERS VIEWS

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        full_name = request.POST.get("full_name")
        state = request.POST.get("state")
        city = request.POST.get("city")
        gender = request.POST.get("gender")
        occupation = request.POST.get("occupation")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("signup")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect("signup")

        user = CustomUser.objects.create_user(username=username, email=email, password=password, role='user')

        verification_code = str(random.randint(100000, 999999))

        Profile.objects.create(
            user=user,
            full_name=full_name,
            state=state,
            city=city,
            gender=gender,
            occupation=occupation,
            verification_code=verification_code,
            code_sent_at=timezone.now()
        )

        email_subject = "Verify Your Email - Ozone Library"
        email_body = f"""
        Hello {full_name},<br><br>
        Your <strong>verification code</strong> is: <strong>{verification_code}</strong><br>
        It will expire in <strong>10 minutes</strong>.<br><br>
        Thank you for joining <b>Ozone Library</b>!
        """

        email_message = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email="nancygrace92@gmail.com",
            to=[email],
        )
        email_message.content_subtype = "html" 
        email_message.send()

        request.session['pending_verification_user_id'] = user.id

        messages.success(request, "Signup successful! A verification code has been sent to your email.")
        return redirect('verify_email')

    return render(request, "signup.html")



def verify_email(request):
    if request.method == "POST":
        verification_code = request.POST.get("verification_code")
        
        user_id = request.session.get('pending_verification_user_id')
        
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                profile = user.profile

                if profile.verification_code == verification_code and (timezone.now() - profile.code_sent_at) < timedelta(minutes=10):
                    user.is_active = True
                    user.save()
                    profile.email_verified = True 
                    profile.save()
                    del request.session['pending_verification_user_id'] 

                    login(request, user)  

                    messages.success(request, "Your email has been successfully verified!")
                    return redirect('user_login')

                else:
                    messages.error(request, "Invalid or expired verification code. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "No pending verification process found. Please try signing up again.")

    return render(request, "verify_email.html")


def resend_verification_code(request):
    user_id = request.session.get('pending_verification_user_id')
    if user_id:
        try:
            user = CustomUser.objects.get(id=user_id)
            profile = user.profile

            new_verification_code = str(random.randint(100000, 999999))

            profile.verification_code = new_verification_code
            profile.code_sent_at = timezone.now()
            profile.save()

            send_mail(
                subject="Verify Your Email",
                message=f"Hello {profile.full_name},\n\nYour new verification code is: {new_verification_code}\nIt expires in 10 minutes.",
                from_email="noreply@ozonelibrary.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, "A new verification code has been sent to your email.")
            return redirect('verify_email')
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
    else:
        messages.error(request, "No pending verification process found.")

    return redirect('signup')



def book_list(request):
    user = request.user

    if getattr(user, 'role', None) in ['librarian', 'receptionist']:
        return HttpResponseForbidden("Access denied: Admins are not allowed to view the user dashboard.")

    borrowed_books = BorrowedBook.objects.values_list("book_id", flat=True)
    available_books = Book.objects.exclude(id__in=borrowed_books)
    user_borrowed_books = BorrowedBook.objects.filter(borrower=user)
    categories = Category.objects.all()

    context = {
        "available_books": available_books,
        "user_borrowed_books": user_borrowed_books,
        "categories": categories,
    }
    return render(request, "book_list.html", context)


@login_required
def books_cat(request, category):
    category_obj = get_object_or_404(Category, name__iexact=category)
    books = Book.objects.filter(category=category_obj)

    context = {
        "category": category_obj.name,
        "books": books
    }

    return render(request, "books_cat.html", context)

@login_required
def book_detail(request, book_id):
    books = Book.objects.filter(id=book_id)
    book_dict = {book.id: {'title': book.title, 'author': book.author, 'category': book.category} for book in books}
    return render(request, 'book_detail.html', {'book_dict': book_dict})

@login_required
def return_book(request, book_id):
    borrowed_book = BorrowedBook.objects.filter(book_id=book_id, borrower=request.user).first()
    if not borrowed_book:
        return JsonResponse({"success": False, "error": "You have not borrowed this book."})

    if request.method == 'POST':
        borrowed_book.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request."})

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if BorrowedBook.objects.filter(book=book, borrower=request.user).exists():
        return JsonResponse({"success": False, "error": "You have already borrowed this book."})

    if request.method == 'POST':
        due_date = date.today() + timedelta(days=3)
        BorrowedBook.objects.create(book=book, borrower=request.user, due_date=due_date)
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request."})


@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']

            if profile_picture.size > 50 * 1024:
                messages.error(request, "File size should not exceed 50KB.")
                return redirect("profile")

            valid_extensions = ["image/jpeg", "image/png", "image/"]
            if profile_picture.content_type not in valid_extensions:
                messages.error(request, "Only JPG, PNG, and JPEG images are allowed.")
                return redirect("profile")

            profile.profile_picture = profile_picture
            profile.save()
            messages.success(request, "Profile picture updated successfully.")

        full_name = request.POST.get('full_name')
        state = request.POST.get('state')
        city = request.POST.get('city')
        gender = request.POST.get('gender')
        occupation = request.POST.get('occupation')

        if full_name:
            profile.full_name = full_name
        if state:
            profile.state = state
        if city:
            profile.city = city
        if gender:
            profile.gender = gender
        if occupation:
            profile.occupation = occupation
        
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "profile.html", {"profile": profile})


@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        state = request.POST.get('state')
        city = request.POST.get('city')
        gender = request.POST.get('gender')
        occupation = request.POST.get('occupation')

        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']

            if profile_picture.size > 50 * 1024:
                messages.error(request, "File size should not exceed 50KB.")
                return redirect("update_profile")

            valid_extensions = ["image/jpeg", "image/png", "image/gif"]
            if profile_picture.content_type not in valid_extensions:
                messages.error(request, "Only JPG, PNG, and JPEG images are allowed.")
                return redirect("update_profile")

            profile.profile_picture = profile_picture

        if full_name:
            profile.full_name = full_name
        if state:
            profile.state = state
        if city:
            profile.city = city
        if gender:
            profile.gender = gender
        if occupation:
            profile.occupation = occupation
        
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "update_profile.html", {"profile": profile})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, 'role') and user.role in ['librarian', 'receptionist']:
                return JsonResponse({"error": "Admins are not allowed to log in from this portal."}, status=403)

            auth_login(request, user)
            return JsonResponse({"message": "Login successful.", "redirect_url": "/dashboard/"})

        return JsonResponse({"error": "Invalid username or password."}, status=401)

    return render(request, "login.html")