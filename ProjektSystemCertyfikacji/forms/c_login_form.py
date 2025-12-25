from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=65, label='Nazwa użytkownika')
    password = forms.CharField(max_length=65, widget=forms.PasswordInput, label='Hasło')
    