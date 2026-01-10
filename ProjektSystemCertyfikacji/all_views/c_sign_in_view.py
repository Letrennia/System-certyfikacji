from django.shortcuts import render, redirect
from ..forms.c_login_form import LoginForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User

def sign_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'company/login.html', {'form': form})
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user_obj = User.objects.get(username=username)
            except User.DoesNotExist:
                # user_obj = None
                messages.error(request, 'Niepoprawna nazwa użytkownika')
                return render(request, 'company/login.html', {'form': form})
            if not user_obj.is_active:
                messages.error(request, 'Twoje konto nie jest jeszcze aktywne')
                return render(request, 'company/login.html', {'form': form})

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Poprawne zalogowanie {username.title()}')
                return redirect('list_cert') #tutaj ma byc strona/widok do formularza z dodawaniem certyfikatow albo jakis panel jednostki certyfikujacej
            else:
                messages.error(request, 'Niepoprawne hasło')

        return render(request, 'company/login.html', {'form': form})