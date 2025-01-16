from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
    

class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='librarian_profile')
    psrn = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.psrn}"


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
        

class Student(models.Model):
    mail = models.CharField(max_length=100, unique=True)
    id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    hostel = models.CharField(max_length=10, default='empty')
    room = models.IntegerField(default=0)
    dues = models.IntegerField(default=0)
    favourites = models.ManyToManyField(Book_Parent, related_name='favourited_by', blank=True)

    def __str__(self):
        return self.name

    
class Book_Borrow(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book_Parent, on_delete=models.CASCADE, related_name='copies')
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    penalty = models.IntegerField(default=0)
    
    @property
    def late_fee(self):
        # Calculate late fee if the return date is past the due date
        settings = LibrarySettings.objects.first()
        if self.borrow_date and not self.is_returned:
            due_date = self.borrow_date + timedelta(days=settings.issue_period)
            if date.today() > self.due_date:
                late_days = (date.today()-self.due_date).days
                late_fees = settings.late_fee_amount * ((1 + settings.fee_compound / 100) ** late_days) # Formula for compounding fees
                return int(late_fees)
        return 0
    
    
    
    @property
    def due_date(self):
        # Calculate late fee if the return date is past the due date
        settings = LibrarySettings.objects.first()
        d_date = self.borrow_date + timedelta(days=settings.issue_period)
        return d_date

    def __str__(self):
        return self.book.title + '-' + str(self.return_date)


class LibrarySettings(models.Model):
    issue_period = models.PositiveIntegerField(default=14)  # Default issue period in days
    late_fee_amount = models.PositiveIntegerField(default=50) # Late fee amount per day
    fee_compound = models.PositiveIntegerField(default=5) # Rate at which fees compound every day
    
    
class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to="feedback_images/", null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    parent_book = models.ForeignKey(Book_Parent, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveIntegerField()
    rated_at = models.DateTimeField(auto_now_add=True)