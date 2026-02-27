from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Certificate, Certifying_unit, Company
from ..forms.certificate_form import CertificateForm
from django.db.models import ProtectedError
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import Certificate_status_history, Certificate
from ..models import Certificate, Certifying_unit, Company, Product_batch

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

    batches = Product_batch.objects.filter(certificate_id=cert)

    return render(request, 'certificates/cert_detail.html', {
        'cert': cert,
        'batches': batches,
    })


@login_required
def edit_cert(request, cert_id):
    try:
        certificate = Certificate.objects.get(certificate_id=cert_id)
    except Certificate.DoesNotExist:
        return render(request, 'certificates/cert_error.html', {
            'msg': 'Certyfikat nie istnieje'
        })
    
    user = request.user
    is_admin = user.is_staff
    
    if not is_admin:
        try:
            user_unit = Certifying_unit.objects.get(user=user)
            if certificate.issued_by_certifying_unit_id != user_unit:
                return render(request, 'certificates/cert_error.html', {
                    'msg': 'Brak uprawnień do edycji tego certyfikatu'
                })
        except Certifying_unit.DoesNotExist:
            return render(request, 'certificates/cert_error.html', {
                'msg': 'Błąd uprawnień'
            })
    
    if request.method == 'GET':
        form = CertificateForm(
            instance=certificate,
            certifying_unit=certificate.issued_by_certifying_unit_id,
            user=user
        )
        
        return render(request, 'certificates/edit_cert.html', {
            'form': form,
            'certificate': certificate,
            'is_admin': is_admin
        })
    
    elif request.method == 'POST':
        form = CertificateForm(
            request.POST, 
            instance=certificate,
            certifying_unit=certificate.issued_by_certifying_unit_id,
            user=user
        )
        
        if form.is_valid():
            cert = form.save()
            messages.success(request, f'Certyfikat {cert.certificate_number} został zaktualizowany pomyślnie')
            return redirect('cert_detail', cert_id=cert.certificate_id)
        else:
            return render(request, 'certificates/edit_cert.html', {
                'form': form,
                'certificate': certificate,
                'is_admin': is_admin,
                'err': 'Błąd - sprawdź poprawność wpisanych danych'
            })

@login_required
def delete_cert(request, cert_id):
    try:
        certificate = Certificate.objects.get(certificate_id=cert_id)
    except Certificate.DoesNotExist:
        return render(request, 'certificates/cert_error.html', {
            'msg': 'Certyfikat nie istnieje'
        })
    
    user = request.user
    is_admin = user.is_staff
    
    if not is_admin:
        try:
            user_unit = Certifying_unit.objects.get(user=user)
            if certificate.issued_by_certifying_unit_id != user_unit:
                return render(request, 'certificates/cert_error.html', {
                    'msg': 'Brak uprawnień do usunięcia tego certyfikatu'
                })
        except Certifying_unit.DoesNotExist:
            return render(request, 'certificates/cert_error.html', {
                'msg': 'Błąd uprawnień'
            })
    
    if request.method == 'GET':
        return render(request, 'certificates/confirm_delete.html', {
            'certificate': certificate
        })
    
    elif request.method == 'POST':
        cert_number = certificate.certificate_number
        
        try:
            certificate.delete()
            messages.success(request, f'Certyfikat {cert_number} został usunięty')
            return redirect('list_cert')
        
        except ProtectedError:
            messages.error(request, 'Nie można usunąć certyfikatu, ponieważ istnieją powiązane partie produktów.')
            return redirect('cert_detail', cert_id=cert_id)

@login_required
def certificate_history_view(request, cert_id):
    """
    Widok historii zmian statusu certyfikatu
    """
    try:
        certificate = Certificate.objects.get(certificate_id=cert_id)
    except Certificate.DoesNotExist:
        return render(request, 'certificates/cert_error.html', {
            'msg': 'Certyfikat nie istnieje'
        })
    
    user = request.user
    is_admin = user.is_staff
    
    if not is_admin:
        try:
            user_unit = Certifying_unit.objects.get(user=user)
            if certificate.issued_by_certifying_unit_id != user_unit:
                return render(request, 'certificates/cert_error.html', {
                    'msg': 'Brak uprawnień do przeglądania historii tego certyfikatu'
                })
        except Certifying_unit.DoesNotExist:
            return render(request, 'certificates/cert_error.html', {
                'msg': 'Błąd uprawnień'
            })
    
    history_records = Certificate_status_history.objects.filter(
        certificate_id=certificate
    ).select_related(
        'changed_by_user_id'
    ).order_by('-changed_date')
    
    status_filter = request.GET.get('status_filter', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_user = request.GET.get('search_user', '')
    
    if status_filter:
        history_records = history_records.filter(new_status=status_filter)
    
    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            history_records = history_records.filter(changed_date__date__gte=date_from_obj.date())
        except ValueError:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            history_records = history_records.filter(changed_date__date__lte=date_to_obj.date())
        except ValueError:
            pass
    
    if search_user:
        history_records = history_records.filter(
            Q(changed_by_user_id__name__icontains=search_user) |
            Q(changed_by_user_id__certifying_unit_code__icontains=search_user)
        )
    
    paginator = Paginator(history_records, 10)  
    page = request.GET.get('page', 1)
    
    try:
        history_page = paginator.page(page)
    except PageNotAnInteger:
        history_page = paginator.page(1)
    except EmptyPage:
        history_page = paginator.page(paginator.num_pages)
    
    total_changes = history_records.count()
    
    from django.db.models import Count
    frequent_changes = history_records.values('old_status', 'new_status').annotate(
        count=Count('history_id')
    ).order_by('-count')[:5]
    
    context = {
        'certificate': certificate,
        'history_records': history_page,
        'total_changes': total_changes,
        'frequent_changes': frequent_changes,
        'current_status_filter': status_filter,
        'current_date_from': date_from,
        'current_date_to': date_to,
        'current_search_user': search_user,
        'status_choices': Certificate_status_history.STATUS,
        'is_admin': is_admin,
        'paginator': paginator,
        'page_obj': history_page,
    }
    
    return render(request, 'certificates/certificate_history.html', context)


@login_required
def certificate_history_export(request, cert_id):
    """
    Eksport historii zmian do formatu JSON
    """
    try:
        certificate = Certificate.objects.get(certificate_id=cert_id)
    except Certificate.DoesNotExist:
        return JsonResponse({'error': 'Certificate not found'}, status=404)
    
    user = request.user
    is_admin = user.is_staff
    
    if not is_admin:
        try:
            user_unit = Certifying_unit.objects.get(user=user)
            if certificate.issued_by_certifying_unit_id != user_unit:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        except Certifying_unit.DoesNotExist:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    
    history_records = Certificate_status_history.objects.filter(
        certificate_id=certificate
    ).select_related(
        'changed_by_user_id'
    ).order_by('-changed_date')
    
    export_data = {
        'certificate': {
            'certificate_id': certificate.certificate_id,
            'certificate_number': certificate.certificate_number,
            'current_status': certificate.get_status_display(),
        },
        'history': [],
        'metadata': {
            'export_date': timezone.now().isoformat(),
            'total_records': history_records.count(),
        }
    }
    
    for record in history_records:
        export_data['history'].append({
            'change_id': record.history_id,
            'timestamp': record.changed_date.isoformat(),
            'old_status': record.get_old_status_display() if record.old_status else 'Brak',
            'new_status': record.get_new_status_display(),
            'changed_by': {
                'unit_id': record.changed_by_user_id.certifying_unit_id,
                'unit_name': record.changed_by_user_id.name,
                'unit_code': record.changed_by_user_id.certifying_unit_code,
            },
            'reason': record.reason,
        })
    
    return JsonResponse(export_data, json_dumps_params={'indent': 2})


@login_required
def certificate_change_log_api(request, cert_id):
    """
    API endpoint dla historii zmian 
    """
    try:
        certificate = Certificate.objects.get(certificate_id=cert_id)
    except Certificate.DoesNotExist:
        return JsonResponse({'error': 'Certificate not found'}, status=404)
    

 
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))
    status_filter = request.GET.get('status', '')
    
    history_query = Certificate_status_history.objects.filter(
        certificate_id=certificate
    ).select_related('changed_by_user_id')
    
    if status_filter:
        history_query = history_query.filter(new_status=status_filter)
    
    total = history_query.count()
    records = history_query.order_by('-changed_date')[offset:offset+limit]
    
    data = {
        'certificate_id': cert_id,
        'certificate_number': certificate.certificate_number,
        'total_changes': total,
        'changes': []
    }
    
    for record in records:
        data['changes'].append({
            'id': record.history_id,
            'timestamp': record.changed_date.isoformat(),
            'old_status': record.get_old_status_display() if record.old_status else 'Brak',
            'new_status': record.get_new_status_display(),
            'changed_by': {
                'id': record.changed_by_user_id.certifying_unit_id,
                'name': record.changed_by_user_id.name,
                'code': record.changed_by_user_id.certifying_unit_code,
            },
            'reason': record.reason,
            'time_ago': naturaltime(record.changed_date),  
        })
    
    return JsonResponse(data)