from django.shortcuts import get_object_or_404, render, redirect
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
import base64
import logging
from ..models import Certificate, Fraud_report, Product_batch, Consumer_verification 
from django.contrib import messages
from ..forms.report_form import FraudReportForm
from ..forms.rating_form import ConsumerRatingForm
from django.db.models import Avg


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
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
        # ratings = certificate.consumer_rating_set.filter(is_verified=1).order_by('-rating_id') 
        
        sort = request.GET.get('sort', 'best')
        ratings = certificate.consumer_rating_set.filter(is_verified=1) 

        if sort == 'worst':
            ratings_sorted = ratings.order_by('rating', '-rating_id')
        elif sort == 'best':
            ratings_sorted = ratings.order_by('-rating', '-rating_id')
        elif sort == 'latest':
            ratings_sorted = ratings.order_by('-rating_id') # Nie mamy daty wiec tak
        elif sort == 'eldest':
            ratings_sorted = ratings.order_by('rating_id')
        
        average_rating = ratings.aggregate(avg=Avg('rating'))['avg']
        average_rating = round(average_rating, 2) if average_rating else None

        if request.method == 'POST' and 'submit_rating' in request.POST:
            rating_form = ConsumerRatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.certificate_id = certificate
                rating.is_verified = 1 
                rating.save()
                messages.success(request, "Twoja opinia została dodana.")
                return redirect('certificate_view', token=token)
        else:
            rating_form = ConsumerRatingForm()
        
        return render(request, 'certificate_detail.html', {
            'certificate': certificate,
            'token': token,
            'ratings': ratings_sorted,
            'average_rating': average_rating,
            'current_sort': sort,
            'rating_form': rating_form
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
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
        
    except Exception as e:
        return render(request, 'certificate_error.html', {
            'message': 'Nieprawidłowy link zgłoszenia.'
        })
    
    if request.method == 'POST':
        form = FraudReportForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['reporter_email']
            # reporter_main = form.cleaned_data['reporter_main'] 
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
            
            partie = Product_batch.objects.filter(certificate_id=certificate)
            
            if partie.exists():
                for partia in partie:
                    fraud_report = Fraud_report.objects.create(
                    certificate_id=certificate,
                    batch_id=partia,  
                    fraud_type=fraud_type,
                    reporter_email=email,
                    description=description,
                    status='new'
                )
                fraud_report.check_and_reject_spam()
            else:
                Fraud_report.objects.create(
                    certificate_id=certificate,
                    batch_id=None,
                    fraud_type=fraud_type,
                    # reporter_main=reporter_main,  
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