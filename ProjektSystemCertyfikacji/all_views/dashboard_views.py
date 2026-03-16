from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Avg, Q, Count
from ..models import Certificate, Consumer_rating, Product_batch, Certifying_unit, Certificate_status_history
from ..models import Fraud_report
from django.utils import timezone
from datetime import timedelta

@login_required
def control_dashboard(request):
    user = request.user
    is_admin = user.is_staff

    if not is_admin and not hasattr(user, 'certifying_unit'):
        return render(request, 'certificates/cert_error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla jednostek certyfikujących i administratorów'
        })

    certificates = Certificate.objects.all().select_related('holder_company_id', 'issued_by_certifying_unit_id')

    if not is_admin:
        try:
            certifying_unit = user.certifying_unit
            certificates = certificates.filter(issued_by_certifying_unit_id=certifying_unit)
        except Certifying_unit.DoesNotExist:
            return render(request, 'certificates/cert_error.html', {
                'msg': 'Błąd - Twoje konto nie jest powiązane z żadną jednostką certyfikującą'
            })

    certificates = certificates.annotate(
        avg_rating=Avg('consumer_rating__rating', filter=Q(consumer_rating__is_verified=1)),
        ratings_count=Count('consumer_rating', filter=Q(consumer_rating__is_verified=1))
    ).order_by('-certificate_id')

    return render(request, 'dashboard/certyfikat_list.html', {
        'certificates': certificates,
        'is_admin': is_admin,
    })

@login_required
def certificate_control_detail(request, cert_id):
    user = request.user
    is_admin = user.is_staff

    certificate = get_object_or_404(Certificate, certificate_id=cert_id)

    if not is_admin:
        if not hasattr(user, 'certifying_unit') or certificate.issued_by_certifying_unit_id != user.certifying_unit:
            return render(request, 'certificates/cert_error.html', {
                'msg': 'Brak uprawnień do tego certyfikatu'
            })

    batches = Product_batch.objects.filter(certificate_id=certificate)
    batches_count = batches.count()
    batches_list = batches.order_by('-production_date')[:10]

    ratings = Consumer_rating.objects.filter(
        certificate_id=certificate,
        is_verified=1
    ).order_by('rating_id')

    rating_values = [r.rating for r in ratings]
    rating_labels = [f'Ocena {i+1}' for i in range(len(ratings))]

    context = {
        'certificate': certificate,
        'batches_count': batches_count,
        'batches': batches_list,
        'rating_values': rating_values,
        'rating_labels': rating_labels,
        'is_admin': is_admin,
    }
    return render(request, 'dashboard/certyfikat_detail.html', context)

@login_required
def revoke_certificate(request, cert_id):
    user = request.user
    is_admin = user.is_staff

    certificate = get_object_or_404(Certificate, certificate_id=cert_id)

    if not is_admin:
        if not hasattr(user, 'certifying_unit') or certificate.issued_by_certifying_unit_id != user.certifying_unit:
            return render(request, 'certificates/cert_error.html', {
                'msg': 'Brak uprawnień do wycofania tego certyfikatu'
            })

    if certificate.status != 'valid':
        messages.error(request, 'Można wycofać tylko certyfikat o statusie "ważny".')
        return redirect('certificate_control_detail', cert_id=cert_id)

    if request.method == 'GET':
        return render(request, 'dashboard/confirm_revoke.html', {
            'certificate': certificate,
            'is_admin': is_admin,
        })

    if request.method == 'POST':
        old_status = certificate.status

        certificate._skip_history = True
        certificate.status = 'revoked'
        certificate.save()

        if is_admin:
            changed_by = certificate.issued_by_certifying_unit_id
            reason_text = f'Wycofanie przez administratora (jednostka: {changed_by.name})'
        else:
            changed_by = user.certifying_unit
            reason_text = 'Wycofanie przez jednostkę certyfikującą'

        Certificate_status_history.objects.create(
            certificate_id=certificate,
            old_status=old_status,
            new_status='revoked',
            changed_by_user_id=changed_by,
            reason=reason_text,
        )

        messages.success(request, f'Certyfikat {certificate.certificate_number} został wycofany.')
        return redirect('control_dashboard')

@staff_member_required
def dashboard_fraud_reports(request):
    all_reports = Fraud_report.objects.select_related(
        'certificate_id', 'batch_id'
    ).order_by('-created_at')

    stats = {
        'total':         all_reports.count(),
        'new':           all_reports.filter(status='new').count(),
        'investigating': all_reports.filter(status='investigating').count(),
        'resolved':      all_reports.filter(status='resolved').count(),
        'rejected':      all_reports.filter(status='rejected').count(),
    }

    pending_reports = all_reports.filter(status__in=['new', 'investigating'])
    recent_reports  = all_reports.exclude(status__in=['new', 'investigating'])

    reports_sections = [
        (pending_reports, 'Do weryfikacji'),
        (recent_reports,  'Ostatnie zgłoszenia'),
    ]

    return render(request, 'dashboard/fraud_reports.html', {
        'stats': stats,
        'reports_sections': reports_sections,
        'pending_reports': pending_reports,
        'recent_reports':  recent_reports,
    })

@staff_member_required
def dashboard_fraud_detail(request, report_id):
    report = Fraud_report.objects.select_related(
        'certificate_id',
        'batch_id',
        'certificate_id__holder_company_id'
    ).get(report_id=report_id)

    return render(request, 'dashboard/fraud_detail.html', {
        'report': report,
        'total_certificates': Certificate.objects.filter(status='valid').count(),
    })
