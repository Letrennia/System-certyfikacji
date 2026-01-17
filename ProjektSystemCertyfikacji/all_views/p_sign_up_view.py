from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from ..forms.p_registration_form import RegisterFormProducer

def sign_up(request):
    if request.method == 'GET':
        form = RegisterFormProducer()
        return render(request, 'entity_log_dir/register_producer.html', {'form': form})
    
    if request.method == 'POST':
        form = RegisterFormProducer(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            messages.success(request, 'poprawna rejestracja')
            login(request, user)
            return redirect('login')
        else:
            return render(request, 'entity_log_dir/register_producer.html', {'form': form})