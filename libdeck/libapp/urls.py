from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.sign_in, name='sign_in'),
    path('student-dashboard', views.student_dashboard, name='student_dashboard'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path('librarian/login/', views.librarian_login, name='librarian_login'),
    path('librarian/dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('add-book/', views.add_book, name='add_book'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('upload-books/', views.upload_books, name='upload_books'),
    path('books/<int:pk>/', views.student_book_details, name='book_details'),
    path('borrow/<int:pk>/', views.borrow_book, name='borrow_book'),
    path('return/<int:borrow_id>/', views.return_book, name='return_book'),
    path('settings/', views.update_library_settings, name='update_library_settings'),
]

if settings.DEBUG:  # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)