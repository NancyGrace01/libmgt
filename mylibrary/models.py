from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('librarian', 'Librarian'),
        ('receptionist', 'Receptionist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.username


class AdminProfile(models.Model):
    ROLE_CHOICES = (
        ('librarian', 'Librarian'),
        ('receptionist', 'Receptionist'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} (Admin)"

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

    @property
    def available(self):
        return not hasattr(self, 'borrowedbook')

    def is_borrowed(self):
        return hasattr(self, 'borrowedbook')

    class Meta:
        ordering = ['title']


def get_due_date():
    return timezone.now() + timedelta(days=3)


class BorrowedBook(models.Model):
    STATUS_CHOICES = [
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
    ]
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(default=get_due_date)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Borrowed')  # <-- Add this line

    def __str__(self):
        return f"{self.borrower.full_name} - {self.book.title}"

    class Meta:
        verbose_name = "Borrowed Book"
        verbose_name_plural = "Borrowed Books"
        ordering = ['-borrow_date']


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=250)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    occupation = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default-profile.png')
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_sent_at = models.DateTimeField(blank=True, null=True)

    def is_code_expired(self):
        if self.code_sent_at:
            return timezone.now() > self.code_sent_at + timedelta(minutes=10)
        return True

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"