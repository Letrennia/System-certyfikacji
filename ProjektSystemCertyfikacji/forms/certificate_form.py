from django import forms
from ..models import Certificate
from ..models import Company
from ..models import Certifying_unit


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            'certificate_number',
            'certificate_type',
            'certificate_publisher',
            'valid_from',
            'valid_to',
            'holder_company_id',
            'issued_by_certifying_unit_id',
            #'blockchain_address',
            'status'
        ]

        widgets = {
            'certificate_number': forms.TextInput(attrs={
                'placeholder': '',
                'class': 'form-control'
            }),
            'certificate_type': forms.TextInput(attrs={
                'placeholder': '',
                'class': 'form-control'
            }),
            'certificate_publisher': forms.TextInput(attrs={
                'placeholder': '',
                'class': 'form-control'
            }),
            'valid_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'valid_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'holder_company_id': forms.Select(attrs={
                'class': 'form-control'
            }),
            'issued_by_certifying_unit_id': forms.Select(attrs={
                'class': 'form-control'
            }),

            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean(self):
        cln_data = super().clean()
        
        vld_from =cln_data.get('valid_from')
        vld_to = cln_data.get('valid_to')

        if vld_from and vld_to and vld_from >= vld_to:
            
            self.add_error('valid_to', 'Data końca musi być po dacie początkowej!')

        return cln_data
