import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from ..models import Producer, RegistrationCode


class RegisterFormProducer(UserCreationForm):
    username = forms.CharField(max_length=150, 
                               label='Nazwa użytkownika',
                               error_messages={
                                   'required': 'To pole jest wymagane',
                                   'unique': 'Ta nazwa użytkownika jest już zajęta'
                               })
    password1 = forms.CharField(widget=forms.PasswordInput, 
                                label='Hasło',
                                error_messages={
                                    'required': 'To pole jest wymagane'
                                })
    password2 = forms.CharField(widget=forms.PasswordInput, 
                                label='Potwierdź hasło',
                                error_messages={
                                    'required': 'To pole jest wymagane'
                                })
    email = forms.EmailField(required=True, 
                             error_messages={
                                'required': 'To pole jest wymagane',
                                'unique': 'Ten email jest już zajęty'
                            })
    name = forms.CharField(max_length=200, label='Nazwa producenta')
    registration_code = forms.CharField(max_length=50, label='Kod weryfikacyjny')
    address = forms.CharField(max_length=500, label='Adres')
    producer_code = forms.CharField(max_length=50, label='Kod producenta')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'registration_code', 
                  'name', 'address', 'producer_code']
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ten email jest zajęty')
        return email
    

    def clean_registration_code(self):
        code = self.cleaned_data['registration_code']

        try:
            reg_code = RegistrationCode.objects.get(code=code, is_used=False)
        except RegistrationCode.DoesNotExist:
            raise forms.ValidationError('Niepoprawny lub zajęty kod weryfikacyjny')

        self._registration_code_obj = reg_code
        return code   
    
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError('Hasło musi mieć conajmniej 8 znaków')
            if not re.search(r'\d', password1):
                raise forms.ValidationError('Hasło musi zawierać przynajmniej jedną cyfrę')
            if not re.search(r'[!@#$%&]', password1):
                raise forms.ValidationError('Hasło musi zawierać przynajmniej jeden znak specjalny')
        return password1
    

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Hasła nie są takie same')
        return password2   
    

    def clean_producer_code(self):
        prod_code = self.cleaned_data['producer_code']
        if Producer.objects.filter(producer_code = prod_code):
            raise forms.ValidationError('Ten kod producenta jest już zajęty')
        return prod_code
    
    def clean_name(self):
        p_name = self.cleaned_data['name']
        if Producer.objects.filter(name = p_name):
            raise forms.ValidationError('Ta nazwa jest już zajęta')
        return p_name
    

    def save(self, commit = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False

        if commit:
            user.save()
            Producer.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                address=self.cleaned_data['address'],
                producer_code=self.cleaned_data['producer_code'],
                is_approved=False
            )

            self._registration_code_obj.is_used = True
            self._registration_code_obj.save()

        return user
    
