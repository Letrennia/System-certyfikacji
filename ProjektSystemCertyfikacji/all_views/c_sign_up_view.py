from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from ..forms.c_registration_form import RegisterForm

def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'company/register.html', {'form': form})
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # user.username = user.username.lower()
            user.save()
            messages.success(request, 'poprawna rejestracja')
            login(request, user)
            return redirect('login')
        else:
            return render(request, 'company/register.html', {'form': form})