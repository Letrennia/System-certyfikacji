from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def sign_out(request):
    logout(request)
    messages.success(request, f'poprawne wylogowanie')
    return redirect('home')
    
