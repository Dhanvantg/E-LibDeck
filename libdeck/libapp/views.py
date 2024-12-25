import os

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from google.oauth2 import id_token
from google.auth.transport import requests

from .models import Student, Book_Parent, Book_Borrow, LibrarySettings, Feedback, Rating
from .forms import student_details, BookForm, BookUploadForm, FeedbackForm

import openpyxl
from datetime import date

@csrf_exempt
def sign_in(request):
    try:
        if request.session['user_data']:
            return redirect('student_dashboard')
    except:
        return render(request, 'sign_in.html')


@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    print('Inside')
    try:
        token = request.POST['credential']
    except:
        return redirect('sign_in')
    
    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID'], clock_skew_in_seconds=15
        )
        print(user_data)
        if user_data['email'].endswith('bits-pilani.ac.in'):
            request.session['user_data'] = user_data
            bits_id = user_data['email'].split('@')[0]
            
            if Student.objects.filter(id=bits_id).exists():
                print('checking')
                if Student.objects.get(id=bits_id).hostel == 'empty':
                    return redirect('student_dashboard')
            else:
                print('creating')
                Student.objects.create(mail = user_data['email'], id = bits_id, name = user_data['name'])
            return redirect('student_dashboard')

        else:
            print('yes')
            return render(request, 'invalid_mail.html')
            
    except Exception as e:
        print(e)
        return redirect('sign_in')


def sign_out(request):
    del request.session['user_data']
    return redirect('sign_in')


def student_dashboard(request):
    bits_id = request.session['user_data']['email'].split('@')[0]
    student = Student.objects.get(id=bits_id)
    books = Book_Parent.objects.all()  # Fetch all books
    query = request.GET.get('q')  # Get the search query from the request
    if query:
        books = Book_Parent.objects.filter(title__icontains=query)
    if request.method == 'POST':
        form = student_details(request.POST, instance=student)  # Bind data from POST request to the form
        if form.is_valid():
            # Access cleaned data
            print('here')
            hostel = form.cleaned_data['hostel']
            room = form.cleaned_data['room']
            student.hostel = hostel
            student.room = room
            student.save()
            
    else:
        print(bits_id, student)
        form = student_details(instance=student)
        
    paginator = Paginator(books, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    borrows = Book_Borrow.objects.filter(student=student)
    # Render the template with the form
    return render(request, 'student_dashboard.html', {'form': form,
        'page_obj': page_obj,
        'query': query,
        'borrows': borrows,})


def student_book_details(request, pk):
    book = get_object_or_404(Book_Parent, pk=pk)
    ratings = book.ratings.all()
    bits_id = request.session['user_data']['email'].split('@')[0]
    student = Student.objects.get(id=bits_id)
    has_rated = Rating.objects.filter(student=student, parent_book=book).exists()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    total_ratings = ratings.count()
    default_rating = None
    eligible = False

    if Book_Borrow.objects.filter(student=student, book=book).count() > 0: 
        eligible = True
        print('yes')
    else:
        print('no')
        eligible = False
    if has_rated:
        default_rating = Rating.objects.get(student=student, parent_book=book).rating
        
    return render(request, 'student_book_details.html', {'book': book, 'avg_rating': avg_rating, 'total_ratings': total_ratings, 'has_rated': has_rated, "default_rating": default_rating, 'eligible': eligible})


def borrow_book(request, pk):
    book = Book_Parent.objects.get(pk=pk)
    bits_id = request.session['user_data']['email'].split('@')[0]
    student = Student.objects.get(id=bits_id)
    if book.available_copies > 0:
        Book_Borrow.objects.create(student=student, book=book)
        book.available_copies -= 1
        book.save()
        messages.success(request, "Book borrowed successfully!")
    else:
        messages.error(request, "No copies of the book are available for borrowing.")
        
    return redirect(request.META.get('HTTP_REFERER'))

def return_book(request, borrow_id):
    borrow = Book_Borrow.objects.get(id=borrow_id)
    borrow.return_date = date.today()
    borrow.is_returned = True
    borrow.save()

    # Update the available copies
    book = borrow.book
    book.available_copies += 1
    book.save()

    return redirect('student_dashboard')


def librarian_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Log in the user
            return redirect('librarian_dashboard')  # Redirect to the dashboard
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'librarian_login.html')


def submit_rating(request, pk):
    book = Book_Parent.objects.get(pk=pk)
    bits_id = request.session['user_data']['email'].split('@')[0]
    student = Student.objects.get(id=bits_id)
    if Rating.objects.filter(student=student, parent_book=book).exists():
        messages.error(request, "You have already rated this book.")
        return redirect("book_details", pk=book.pk)
    
    if request.method == "POST":
        rating_value = request.POST.get("rating")
        if rating_value:
            Rating.objects.create(
                student=student,
                parent_book=book,
                rating=int(rating_value)
            )
            messages.success(request, "Thank you for your rating!")
            return redirect("book_details", pk=book.pk)
        else:
            messages.error(request, "Please select a rating before submitting.")
            return redirect("book_details", book_id=book.pk)
    return render(request, "submit_rating.html", {"book": book})


def submit_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            bits_id = request.session['user_data']['email'].split('@')[0]
            feedback.student = Student.objects.get(id=bits_id)
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect("student_dashboard")
    else:
        form = FeedbackForm()
    return render(request, "submit_feedback.html", {"form": form})


@login_required
def librarian_dashboard(request):
    books = Book_Parent.objects.all()  # Fetch all books
    query = request.GET.get('q')  # Get the search query from the request
    feedbacks = Feedback.objects.all().order_by("-submitted_at")
    print(feedbacks)
    if query:
        books = Book_Parent.objects.filter(title__icontains=query)  # Filter books by title
        
    paginator = Paginator(books, 2)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'librarian_dashboard.html', {
        'username': request.user.username,
        'psrn': request.user.psrn,
        'books': books,
        'page_obj': page_obj,
        'query': query,
        'feedbacks': feedbacks,
    })
    
@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
            return redirect('librarian_dashboard') 
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book_Parent, pk=pk)  # Get the book by primary key
    borrows = Book_Borrow.objects.filter(book=book, is_returned=False)
    available_copies = book.total_copies - borrows.count()
    ratings = book.ratings.all()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    total_ratings = ratings.count()
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            book.available_copies = available_copies
            book.save()
            print(available_copies, book.available_copies)
            messages.success(request, "Book details updated successfully!")
            return redirect('librarian_dashboard')  # Redirect to the dashboard or another page
    else:
        form = BookForm(instance=book)  # Pre-fill the form with the current book data
    
    borrows = [borrow for borrow in borrows]
    return render(request, 'book_detail.html', {'form': form, 'book': book, 'available_copies': available_copies, 'borrows': borrows, 'avg_rating': avg_rating, 'total_ratings': total_ratings})

@login_required
def delete_book(request, pk):
    book = get_object_or_404(Book_Parent, pk=pk)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect('librarian_dashboard')
    return render(request, 'delete_book_confirm.html', {'book': book})

@login_required
def upload_books(request):
    if request.method == "POST":
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["excel_file"]

            # Open the uploaded Excel file
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active

                for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header row
                    title, author, publisher, isbn, publication_year, total_copies = row

                    if isbn and Book_Parent.objects.filter(isbn=isbn).exists():
                        messages.error(request, f"Error: ISBN {isbn} already exists for another book.")
                        continue
                    
                    # Ensure required fields are present
                    if title and author and total_copies:
                        book = Book_Parent(
                            title=title,
                            author=author,
                            publisher=publisher,
                            isbn=isbn,
                            publication_year=publication_year,
                            total_copies=total_copies,
                            available_copies=total_copies,
                        )
                        book.save()

                messages.success(request, "Books uploaded successfully!")
                return redirect("librarian_dashboard")

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")

    else:
        form = BookUploadForm()

    return render(request, "upload_books.html", {"form": form})


@login_required
def update_library_settings(request):
    settings = LibrarySettings.objects.first()
    if settings is None:
        # Create a default LibrarySettings record if none exist
        settings = LibrarySettings.objects.create(issue_period=14, late_fee_amount=50)
    if request.method == 'POST':
        issue_period = request.POST.get('issue_period')
        late_fee_amount = request.POST.get('late_fee_amount')
        settings.issue_period = int(issue_period)
        settings.late_fee_amount = float(late_fee_amount)
        settings.save()
        return redirect('librarian_dashboard')  # Redirect to librarian dashboard

    return render(request, 'update_settings.html', {'settings': settings})

