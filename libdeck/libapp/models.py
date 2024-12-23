from django.db import models
from django.contrib.auth.models import AbstractUser

class Student(models.Model):
    mail = models.CharField(max_length=100, unique=True)
    id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    hostel = models.CharField(max_length=10, default='empty')
    room = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
    

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
        
    
    
class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
    ]
    parent_book = models.ForeignKey(Book_Parent, on_delete=models.CASCADE, related_name='copies')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    borrower = models.CharField(max_length=100, null=True, blank=True)  # Reference BITS ID
    due_date = models.DateField(null=True, blank=True)
    
    

    def __str__(self):
        return self.title
