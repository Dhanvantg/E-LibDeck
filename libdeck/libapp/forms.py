from django import forms

class student_details(forms.Form):
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
