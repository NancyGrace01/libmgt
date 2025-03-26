from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Book(models.Model):
    CATEGORIES = [
        ('fiction', 'Fiction'),
        ('nonfiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
    ]
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class BorrowedBook(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(default=timezone.now() + timedelta(days=3))
    def __str__(self):
        return f"{self.book.title} borrowed by {self.borrower.username}"    

