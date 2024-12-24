import os

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from .models import Student, Book_Parent
from .forms import student_details, BookForm, BookUploadForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import openpyxl

@csrf_exempt
def sign_in(request):
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
                    return redirect('submit_form')
            else:
                print('creating')
                Student.objects.create(mail = user_data['email'], id = bits_id, name = user_data['name'])
            return redirect('sign_in')

        else:
            print('yes')
            return render(request, 'invalid_mail.html')
            
    except Exception as e:
        print(e)
        return redirect('sign_in')


def sign_out(request):
    del request.session['user_data']
    return redirect('sign_in')


def student_form(request):
    if request.method == 'POST':
        form = student_details(request.POST)  # Bind data from POST request to the form
        if form.is_valid():
            # Access cleaned data
            print('here')
            hostel = form.cleaned_data['hostel']
            room = form.cleaned_data['room']
            bits_id = request.session['user_data']['email'].split('@')[0]
            Student.objects.filter(id=bits_id).update(hostel=hostel, room=room)
            
            return redirect('sign_in')
            
    else:
        form = student_details()

    # Render the template with the form
    return render(request, 'student_details.html', {'form': form})



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


@login_required
def librarian_dashboard(request):
    books = Book_Parent.objects.all()  # Fetch all books
    query = request.GET.get('q')  # Get the search query from the request
    if query:
        books = Book_Parent.objects.filter(title__icontains=query)  # Filter books by title
    else:
        books = Book_Parent.objects.all()
    return render(request, 'librarian_dashboard.html', {
        'username': request.user.username,
        'psrn': request.user.psrn,
        'books': books,
        'query': query,
    })
    
    
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


def book_detail(request, pk):
    book = get_object_or_404(Book_Parent, pk=pk)  # Get the book by primary key
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book details updated successfully!")
            return redirect('librarian_dashboard')  # Redirect to the dashboard or another page
    else:
        form = BookForm(instance=book)  # Pre-fill the form with the current book data
    return render(request, 'book_detail.html', {'form': form, 'book': book})


def delete_book(request, pk):
    book = get_object_or_404(Book_Parent, pk=pk)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect('librarian_dashboard')
    return render(request, 'delete_book_confirm.html', {'book': book})


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