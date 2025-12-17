from django.shortcuts import get_object_or_404, render, redirect
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
import base64
import logging
from .models import Certificate, Fraud_report, Product_batch
from django.contrib import messages
from .forms import FraudReportForm

logger = logging.getLogger(__name__)

def decrypt_token(token):
    try:
        padding_needed = len(token) % 4
        if padding_needed:
            token += '=' * (4 - padding_needed)
        
        encrypted_data = base64.urlsafe_b64decode(token.encode())
        f = Fernet(settings.FERNET_KEY)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode()
    except Exception as e:
        raise ValueError(f"Błąd deszyfrowania tokenu: {str(e)}")

def certificate_view(request, token):
    try:
        certificate_id = decrypt_token(token)
        certificate = get_object_or_404(Certyfikat, certificate_id=certificate_id)
        
        return render(request, 'certificate_detail.html', {
            'certificate': certificate,
            'token': token
        })
        
    except ValueError as e:
        logger.error(f"Błąd tokenu: {str(e)}")
        return render(request, 'certificate_error.html', {
            'message': 'Nieprawidłowy lub uszkodzony link certyfikatu.'
        })
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {str(e)}")
        return render(request, 'certificate_error.html', {
            'message': 'Wystąpił nieoczekiwany błąd.'
        })

def report_fraud(request, token):
    try:
        certificate_id = decrypt_token(token)
        certificate = get_object_or_404(Certyfikat, certificate_id=certificate_id)
        
    except Exception as e:
        return render(request, 'certificate_error.html', {
            'message': 'Nieprawidłowy link zgłoszenia.'
        })
    
    if request.method == 'POST':
        form = FraudReportForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['reporter_email']
            reporter_main = form.cleaned_data['reporter_main'] 
            fraud_type = form.cleaned_data['fraud_type']
            description = form.cleaned_data['description']
            
            already_reported = Fraud_report.objects.filter(
                certificate_id=certificate,
                reporter_email=email
            ).exists()
            
            if already_reported:
                return render(request, 'report_fraud.html', {
                    'certificate': certificate,
                    'form': form,
                    'error': 'Ten certyfikat został już zgłoszony z tego adresu email.',
                    'token': token
                })
            
            partie = Partia_produktow.objects.filter(certificate_id=certificate)
            
            if partie.exists():
                for partia in partie:
                    Fraud_report.objects.create(
                        certificate_id=certificate,
                        batch_id=partia,  
                        fraud_type=fraud_type,
                        reporter_main=reporter_main,  
                        reporter_email=email,
                        description=description,
                        status='new'
                    )
            else:
                Fraud_report.objects.create(
                    certificate_id=certificate,
                    batch_id=None,
                    fraud_type=fraud_type,
                    reporter_main=reporter_main,  
                    reporter_email=email,
                    description=description,
                    status='new'
                )
            
            return redirect('certificate_view', token=token)
    else:
        form = FraudReportForm()
    
    return render(request, 'report_fraud.html', {
        'form': form,
        'certificate': certificate,
        'token': token
    })