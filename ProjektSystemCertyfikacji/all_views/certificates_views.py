from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Certificate, Certifying_unit, Company
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
        form = CertificateForm(certifying_unit=certifying_unit, user=request.user)
        return render(request, 'certificates/add_cert.html', {
            'form': form,
            'is_admin': is_admin
        })
    
    if request.method == 'POST':
        form = CertificateForm(request.POST, certifying_unit=certifying_unit, user=request.user)
        if form.is_valid():
            cert = form.save(commit=False)
            
            if not is_admin:
                cert.issued_by_certifying_unit_id = certifying_unit
            
            cert.save()
            form.save_m2m()
            
            messages.success(request, f'Certyfikat {cert.certificate_number} został poprawnie dodany')
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

@login_required
def list_cert(request):
    user = request.user
    is_admin = user.is_staff
    
    certificates = Certificate.objects.all().select_related(
        'issued_by_certifying_unit_id', 
        'holder_company_id'
    ).prefetch_related('activity_areas')
    
    if not is_admin:
        try:
            certifying_unit = Certifying_unit.objects.get(user=user)
            certificates = certificates.filter(issued_by_certifying_unit_id=certifying_unit)
        except Certifying_unit.DoesNotExist:
            return render(request, 'certificates/cert_error.html', {
                'msg': 'Błąd - Twoje konto nie jest powiązane z żadną jednostką certyfikującą'
            })
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort_by', 'valid_from')
    sort_order = request.GET.get('sort_order', 'asc')
    issued_by_search = request.GET.get('issued_by_search', '')
    company_search = request.GET.get('company_search', '')
    
    if search:
        certificates = certificates.filter(certificate_number__icontains=search)
    
    if status_filter:
        certificates = certificates.filter(status=status_filter)
    
    if company_search:
        certificates = certificates.filter(holder_company_id__name__icontains=company_search)
    
    if is_admin and issued_by_search:
        certificates = certificates.filter(issued_by_certifying_unit_id__name__icontains=issued_by_search)
    
    if sort_order == 'desc':
        certificates = certificates.order_by(f'-{sort_by}')
    else:
        certificates = certificates.order_by(sort_by)
    
    status_choices = Certificate.STATUS
    certifying_units = Certifying_unit.objects.all() if is_admin else None
    companies = Company.objects.all()
    
    return render(request, 'certificates/list_cert.html', {
        'certy': certificates,
        'current_search': search,
        'current_status': status_filter,
        'current_sort': sort_by,
        'current_order': sort_order,
        'current_issued_by_search': issued_by_search,
        'current_company_search': company_search,
        'status_choices': status_choices,
        'certifying_units': certifying_units,
        'companies': companies,
        'is_admin': is_admin
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