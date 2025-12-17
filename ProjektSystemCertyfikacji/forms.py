from django import forms
from .models import Fraud_report

class FraudReportForm(forms.ModelForm):
    class Meta:
        model = Fraud_report
        fields = ['fraud_type', 'reporter_email', 'description']
        widgets = {
            'fraud_type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Wybierz typ oszustwa'
            }),
            'reporter_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Podaj swój email'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Opisz szczegółowo podejrzenie oszustwa...',
                'rows': 4
            }),
        }
        labels = {
            'fraud_type': 'Typ oszustwa',
            'reporter_email': 'Twój email',
            'description': 'Opis'
        }