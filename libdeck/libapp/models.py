from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    mail = models.CharField(max_length=100, unique=True)
    id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    hostel = models.CharField(max_length=10, default='empty')
    room = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
    

