from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Certificate, Certifying_unit
from ..forms.certificate_form import CertificateForm

@login_required
def add_cert(request):
    user = request.user
    is_admin = user.is_staff
    
    certifying_unit = None
    if not is_admin:
        try:
            certifying_unit = Certifying_unit.objects.get(user=user)
        except Certifying_unit.DoesNotExist:
            return render(request, 'certificates/cert_error.html', {
                'msg': 'Błąd - Twoje konto nie jest powiązane z żadną jednostką certyfikującą'
            })
    
    if request.method == 'GET':
        form = CertificateForm(certifying_unit=certifying_unit, is_admin=is_admin)
        return render(request, 'certificates/add_cert.html', {
            'form': form,
            'is_admin': is_admin
        })
    
    if request.method == 'POST':
        form = CertificateForm(request.POST, certifying_unit=certifying_unit, is_admin=is_admin)
        if form.is_valid():
            cert = form.save(commit=False)
            
            if not is_admin:
                cert.issued_by_certifying_unit_id = certifying_unit
            
            cert_num = cert.certificate_number
            cert.qr_code_data = f"https://example.com/cert/{cert_num}/"
            cert.save()
            
            messages.success(request, f'Certyfikat {cert_num} został poprawnie dodany')
            return redirect('cert_succes', cert_id=cert.certificate_id)
        else:
            return render(request, 'certificates/add_cert.html', {
                'form': form,
                'err': 'Błąd - sprawdź poprawność danych',
                'is_admin': is_admin
            })

def cert_succes(request, cert_id):
    try:
        cert = Certificate.objects.get(certificate_id=cert_id)
    except Certificate.DoesNotExist:
        return render(request, 'certificates/cert_error.html', {
            'msg': 'Błąd - certyfikat nie znaleziony'
        })
    
    return render(request, 'certificates/cert_succes.html', {
        'cert': cert
    })

def list_cert(request):
    certy = Certificate.objects.all()
    return render(request, 'certificates/list_cert.html', {
        'certy': certy
    })

def cert_detail(request, cert_id):
    try:
        cert = Certificate.objects.get(certificate_id=cert_id)
    except Certificate.DoesNotExist:
        return render(request, 'certificates/cert_error.html', {
            'msg': 'Certyfikat nie znaleziony'
        })
    
    return render(request, 'certificates/cert_detail.html', {
        'cert': cert
    })
