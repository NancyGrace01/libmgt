from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.book_list, name='book_list'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:book_id>/', views.return_book, name='return_book'),
    path('books/<str:category>/', views.books_cat, name='books_cat'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('resend_verification_code/', views.resend_verification_code, name='resend_verification_code'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='user_login'), name='logout'),
    path('admin-register/', views.admin_register, name="admin_register"),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('borrowed-books/', views.borrowed_books, name='borrowed_books'),
    path('books/', views.books, name='books'),
    path('add-book/', views.add_book, name='add_book'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('edit-book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('categories/', views.category_list, name='category_list'),
    path('add-categories', views.add_category, name='add_category'),
    path('cat-delete/<int:category_id>/', views.cat_delete, name='cat_delete'),
    path('users-list/', views.users_list, name='users_list'),
    path('users-edit/<int:profile_id>/', views.edit_user, name='edit_user'),
    path('users-delete/<int:profile_id>/', views.delete_user, name='delete_user'),    

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
