from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

class Student(models.Model):
    mail = models.CharField(max_length=100, unique=True)
    id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    hostel = models.CharField(max_length=10, default='empty')
    room = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

class Librarian(AbstractUser):
    psrn = models.CharField(max_length=20, null=True, blank=True, unique=True)
    name = models.CharField(max_length=100)
    REQUIRED_FIELDS = ["psrn"]
    def __str__(self):
        return f"{self.name} ({self.psrn})"


class Book_Parent(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    publication_year = models.IntegerField()
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Set available_copies to total_copies if not already set
        if self.pk is None or self.available_copies is None: 
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)
        
    
    
class Book_Borrow(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book_Parent, on_delete=models.CASCADE, related_name='copies')
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    
    @property
    def late_fee(self):
        # Calculate late fee if the return date is past the due date
        settings = LibrarySettings.objects.first()
        if self.borrow_date:
            due_date = self.borrow_date + timedelta(days=settings.issue_period)
            if self.borrow_date > due_date:
                late_days = (self.borrow_date - due_date).days
                return late_days * settings.late_fee_amount
        return 0
    
    @property
    def due_date(self):
        # Calculate late fee if the return date is past the due date
        settings = LibrarySettings.objects.first()
        d_date = self.borrow_date + timedelta(days=settings.issue_period)
        return d_date

    def __str__(self):
        return self.student


class LibrarySettings(models.Model):
    issue_period = models.PositiveIntegerField(default=14)  # Default issue period in days
    late_fee_amount = models.PositiveIntegerField(default=50) # Late fee amount per day
    
    
