from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
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
