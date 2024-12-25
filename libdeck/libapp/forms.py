from django import forms
from .models import Book_Parent, Student, Feedback

class student_details(forms.ModelForm):
    choices = [
        ('SR', 'SR'),
        ('Gandhi', 'Gandhi'),
        ('Krishna', 'Krishna'),
        ('Vyas', 'Vyas'),
        ('Bhagirath', 'Bhagirath'),
        ('Ram', 'Ram'),
        ('Buddh', 'Buddh'),
        ('Meera', 'Meera'),
        ('Malaviya', 'Malaviya'),
        ('RP', 'RP'),
        ('Ashok', 'Ashok'),
        ('VK', 'VK'),
    ]
    hostel = forms.ChoiceField(choices=choices, label='Select Hostel')
    room = forms.IntegerField(label="Room Number")
    
    class Meta:
        model = Student
        fields = ['hostel', 'room']


class BookForm(forms.ModelForm):
    class Meta:
        model = Book_Parent
        fields = ['title', 'author', 'publisher', 'isbn', 'publication_year', 'total_copies', 'cover_image']
        
        
class BookUploadForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")
    
    
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'body', 'image']