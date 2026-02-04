import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from ..models import Company, RegistrationCode

class RegisterFormCompany(UserCreationForm):
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
    name = forms.CharField(max_length=200, label='Nazwa firmy')
    company_type = forms.ChoiceField(choices=Company.COMPANY_TYPE, label="Typ firmy")
    address = forms.CharField(max_length=500, label='Adres')
    country = forms.CharField(max_length=100, label="Kraj")
    registration_number = forms.CharField(max_length=50, label="Numer rejestracyjny")
    phone = forms.CharField(max_length=20, label="Telefon")
    website = forms.CharField(max_length=255, label="Strona www")
    registration_code = forms.CharField(max_length=50, label='Kod weryfikacyjny')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


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
    
    # def clean_company_code(self):
    #     company_code = self.cleaned_data['company_code']
    #     if Company.objects.filter(company_code = company_code):
    #         raise forms.ValidationError('Ten kod jest już zajęty')
    #     return company_code

    def clean_name(self):
        company_name = self.cleaned_data['name']
        if Company.objects.filter(name = company_name):
            raise forms.ValidationError('Ta nazwa jest już zajęta')
        return company_name
    
    def clean_phone(self):
        phone_n = self.cleaned_data['phone']
        if not phone_n.isdigit():
            raise forms.ValidationError('Niepoprawny numer')
        return phone_n
    
    def clean_website(self):
        website = self.cleaned_data['website']
        pattern = r'^www\..+\.[a-z]{2,}$'
        if not re.match(pattern, website):
            raise forms.ValidationError('Niepoprawny adres strony')
        return website
    

    def save(self, commit = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False

        if commit:
            user.save()
            Company.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                email=self.cleaned_data['email'],
                company_type=self.cleaned_data['company_type'],
                address=self.cleaned_data['address'],
                country=self.cleaned_data['country'],
                registration_number=self.cleaned_data['registration_number'],
                phone=self.cleaned_data['phone'],
                website=self.cleaned_data['website'],
                # company_code=self.cleaned_data['company_code'],
                is_approved=False
            )

            self._registration_code_obj.is_used = True
            self._registration_code_obj.save()

        return user


