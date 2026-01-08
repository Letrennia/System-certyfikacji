from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Certificate
from ..forms.certificate_form import CertificateForm


@login_required
def add_cert(request):
    if request.method == 'GET':
        form = CertificateForm()
        return render(request, 'certificates/add_cert.html', {
            'form': form
        })


    if request.method == 'POST':
        form = CertificateForm(request.POST)

        if form.is_valid():
            cert = form.save(commit=False)
            
            cert_num = cert.certificate_number
            cert.qr_code_data = f"https://example.com/cert/{cert_num}/"
            
            cert.save()
            
            messages.success(request, f'Certyfikat {cert_num} został poprawnie dodany')
            return redirect('cert_succes', cert_id=cert.certificate_id)

        else:
            return render(request, 'certificates/add_cert.html', {
                'form': form,
                'err': 'Błąd - sprawdź poprawność danych'
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

