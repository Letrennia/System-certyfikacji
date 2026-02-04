from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from ..forms.company_registration_form import RegisterFormCompany

def sign_up(request):
    if request.method == 'GET':
        form = RegisterFormCompany()
        return render(request, 'entity_log_dir/register_company.html', {'form': form})
    
    if request.method == 'POST':
        form = RegisterFormCompany(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            messages.success(request, 'poprawna rejestracja')
            login(request, user)
            return redirect('login')
        else:
            return render(request, 'entity_log_dir/register_company.html', {'form': form})