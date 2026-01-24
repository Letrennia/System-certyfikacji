from django import forms
from ..models import Consumer_rating
from captcha.fields import CaptchaField

class ConsumerRatingForm(forms.ModelForm):
    captcha_field = CaptchaField(error_messages={'invalid': 'Niepoprawna captcha.'})
    class Meta:
        model = Consumer_rating
        fields = ['consumer_email', 'rating', 'comment']
        widgets = {
            'consumer_email': forms.EmailInput(attrs={'placeholder': ''}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'placeholder': ''}),
        }
