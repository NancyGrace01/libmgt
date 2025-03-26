from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Book, BorrowedBook
from datetime import timedelta, date
from django.db.models import Q



def home(request):
    return render(request, 'book_list.html')  

def is_librarian(user):
    return user.is_staff

@user_passes_test(is_librarian)
def add_book(request):
    pass


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


# def book_list(request):
#     borrowed_book_ids = BorrowedBook.objects.values_list("book_id", flat=True).distinct()
#     available_books = Book.objects.exclude(id__in=borrowed_book_ids)
#     user_borrowed_books = BorrowedBook.objects.filter(borrower=request.user)

#     context = {
#         "available_books": available_books,
#         "borrowed_books": user_borrowed_books
#     }
#     return render(request, "book_list.html", context)

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
        return render(request, 'return_book.html', {'error': 'You have not borrowed this book or it has already been returned.'})
    if request.method == 'POST':
        borrowed_book.delete()
        return redirect('book_list')

    return render(request, 'return_book.html', {'book': borrowed_book.book})

