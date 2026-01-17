from django import forms

from ..models import Certificate
from ..models import Company
from ..models import Certifying_unit
from ..models import Activity_area

class CertificateForm(forms.ModelForm):
    activity_areas = forms.ModelMultipleChoiceField(
        queryset=Activity_area.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Działalność"
    )
    
    class Meta:
        model = Certificate
        fields = [

            'certificate_number',
            'valid_from',
            'valid_to',
            'holder_company_id',
            'issued_by_certifying_unit_id',
            #'blockchain_address',
            'status',
            'activity_areas',
            'subject_type',
        ]

        widgets = {
            'certificate_number': forms.TextInput(attrs={
                'placeholder': 'np. CERT-2025-001',
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
            }),
            'activity_areas': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'subject_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, certifying_unit=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user and certifying_unit and not user.is_superuser:
            self.fields['issued_by_certifying_unit_id'].initial = certifying_unit
            self.fields['issued_by_certifying_unit_id'].queryset = \
                Certifying_unit.objects.filter(
                    certifying_unit_id=certifying_unit.certifying_unit_id
                )

        

    def clean(self):
        cln_data = super().clean()
        vld_from = cln_data.get('valid_from')
        vld_to = cln_data.get('valid_to')
        
        if vld_from and vld_to and vld_from >= vld_to:
            self.add_error('valid_to', 'Data końca musi być po dacie początkowej!')
        
        return cln_data