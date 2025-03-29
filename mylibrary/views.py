from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages
from .models import Book, BorrowedBook, Profile
from django.contrib.auth.models import User
from datetime import timedelta, date
from django.http import JsonResponse
from django.core.files.storage import default_storage



def home(request):
    return render(request, 'book_list.html')  

def is_librarian(user):
    return user.is_staff

@user_passes_test(is_librarian)
def add_book(request):
    pass



def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
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

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("signup")

        user = User.objects.create_user(username=username, password=password)

        Profile.objects.create(
            user=user,
            full_name=full_name,
            state=state,
            city=city,
            gender=gender,
            occupation=occupation
        )

        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, "Signup successful! Welcome to the platform.")
            return redirect("login")

    return render(request, "signup.html")


def book_list(request):
    user = request.user
    borrowed_books = BorrowedBook.objects.values_list("book_id", flat=True)
    available_books = Book.objects.exclude(id__in=borrowed_books)
    user_borrowed_books = BorrowedBook.objects.filter(borrower=user)

    context = {
        "available_books": available_books,
        "user_borrowed_books": user_borrowed_books
    }
    return render(request, "book_list.html", context)



@login_required
def books_cat(request, category):
    books = Book.objects.filter(category__iexact=category)

    context = {
        "category": category,
        "books": books
    }

    return render(request, "books_cat.html", context)

@login_required
def book_detail(request, book_id):
    books = Book.objects.filter(id=book_id)
    book_dict = {book.id: {'title': book.title, 'author': book.author, 'category': book.category} for book in books}
    return render(request, 'book_detail.html', {'book_dict': book_dict})


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if BorrowedBook.objects.filter(book=book, borrower=request.user).exists():
        return render(request, 'borrow_book.html', {'book': book, 'error': 'You have already borrowed this book.'})
    if request.method == 'POST':
        due_date = date.today() + timedelta(days=3)
        BorrowedBook.objects.create(book=book, borrower=request.user, due_date=due_date)
        return redirect('book_list')
    
    return render(request, 'borrow_book.html', {'book': book})


@login_required
def return_book(request, book_id):
    borrowed_book = BorrowedBook.objects.filter(book_id=book_id, borrower=request.user).first()
    if not borrowed_book:
        return render(request, 'return_book.html', {'error': 'You have not borrowed this book.'})
    if request.method == 'POST':
        borrowed_book.delete()
        return redirect('book_list')

    return render(request, 'return_book.html', {'book': borrowed_book.book})


@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']

            if profile_picture.size > 50 * 1024:
                messages.error(request, "File size should not exceed 50KB.")
                return redirect("profile")

            valid_extensions = ["image/jpeg", "image/png", "image/gif"]
            if profile_picture.content_type not in valid_extensions:
                messages.error(request, "Only JPG, PNG, and GIF images are allowed.")
                return redirect("profile")

            profile.profile_picture = profile_picture
            profile.save()
            messages.success(request, "Profile picture updated successfully.")
            return redirect("profile") 

    return render(request, "profile.html", {"profile": profile})




def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful.")
            return JsonResponse({"success": True, "message": "Login successful."})
        else:
            messages.error(request, "Invalid username or password.")
            return JsonResponse({"success": False, "message": "Invalid username or password."})
    
    return render(request, "login.html")