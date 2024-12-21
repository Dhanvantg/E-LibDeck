import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from .models import Student
from .forms import student_details

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
