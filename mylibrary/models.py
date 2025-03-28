from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=250)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    occupation = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default-profile.png')

    def __str__(self):
        return self.user.username
