from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.book_list, name='book_list'),
    path('profile/', views.profile, name='profile'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:book_id>/', views.return_book, name='return_book'),
    path('books/<str:category>/', views.books_cat, name='books_cat'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
]


