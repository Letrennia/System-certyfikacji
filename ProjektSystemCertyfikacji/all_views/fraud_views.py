from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..models import Fraud_report, Product_batch
from ..serializers import FraudReportSerializer

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from ..forms.report_form import FraudReportForm
from ..models import Certifying_unit
# from ..utils.redirect_certificate_url import encrypt_certificate_id

@method_decorator(csrf_exempt, name='dispatch')
class FraudReportViewSet(viewsets.ModelViewSet):
    queryset = Fraud_report.objects.all().select_related('certificate_id', 'batch_id')
    serializer_class = FraudReportSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        fraud_type = self.request.query_params.get('fraud_type')
        if fraud_type:
            queryset = queryset.filter(fraud_type=fraud_type)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(reporter_email__icontains=search) |
                Q(description__icontains=search) |
                Q(certificate_id__certificate_number__icontains=search) |
                Q(batch_id__name__icontains=search)
            )

        certificate_id = self.request.query_params.get('certificate_id')
        if certificate_id:
            queryset = queryset.filter(certificate_id=certificate_id)

        batch_id = self.request.query_params.get('batch_id')
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        now = timezone.now()

        total = Fraud_report.objects.count()
        last_24h = Fraud_report.objects.filter(created_at__gte=now - timedelta(days=1)).count()
        last_7d = Fraud_report.objects.filter(created_at__gte=now - timedelta(days=7)).count()

        by_status = Fraud_report.objects.values('status').annotate(
            count=Count('status')
        ).order_by('status')

        by_type = Fraud_report.objects.values('fraud_type').annotate(
            count=Count('fraud_type')
        ).order_by('fraud_type')

        top_certificates = Fraud_report.objects.values(
            'certificate_id__certificate_id',
            'certificate_id__certificate_number'
        ).annotate(
            count=Count('certificate_id')
        ).exclude(certificate_id__isnull=True).order_by('-count')[:5]

        daily_stats = Fraud_report.objects.filter(
            created_at__gte=now - timedelta(days=30)
        ).extra(
            {'day': "date(created_at)"}
        ).values('day').annotate(
            count=Count('report_id')
        ).order_by('day')

        return Response({
            'total': total,
            'last_24h': last_24h,
            'last_7d': last_7d,
            'by_status': by_status,
            'by_type': by_type,
            'top_certificates': top_certificates,
            'daily_stats': daily_stats,
        })

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        report_ids = request.data.get('report_ids', [])
        new_status = request.data.get('status')

        if not report_ids:
            return Response(
                {'error': 'Nie podano ID zgłoszeń'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in dict(Fraud_report.STATUS).keys():
            return Response(
                {'error': 'Nieprawidłowy status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated = Fraud_report.objects.filter(report_id__in=report_ids).update(
            status=new_status
        )

        return Response({
            'message': f'Zaktualizowano {updated} zgłoszeń',
            'updated_count': updated
        })

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        report = self.get_object()
        note = request.data.get('note')

        if not note:
            return Response(
                {'error': 'Notatka nie może być pusta'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        new_note = f"\n[{timestamp}] {user}: {note}"

        if report.investigation_notes:
            report.investigation_notes += new_note
        else:
            report.investigation_notes = new_note.lstrip('\n')

        report.save()

        return Response({
            'message': 'Notatka dodana',
            'investigation_notes': report.investigation_notes
        })


def _get_can_edit(request, certificate):
    """Helper — sprawdza czy zalogowany user może edytować dany certyfikat."""
    if not request.user.is_authenticated:
        return False
    if request.user.is_staff:
        return True
    try:
        user_unit = Certifying_unit.objects.get(user=request.user)
        return certificate.issued_by_certifying_unit_id == user_unit
    except Certifying_unit.DoesNotExist:
        return False


@csrf_exempt
@require_http_methods(["POST"])
def submit_fraud_report_html(request, certificate_id):
    from ..models import Certificate

    try:
        certificate = Certificate.objects.get(certificate_id=certificate_id)
    except Certificate.DoesNotExist:
        messages.error(request, 'Certyfikat nie istnieje')
        return redirect('main_page')

    form = FraudReportForm(request.POST)

    if form.is_valid():
        fraud_report = form.save(commit=False)
        fraud_report.certificate_id = certificate

        if not fraud_report.investigation_notes:
            fraud_report.investigation_notes = ''

        fraud_report.save()
        fraud_report.check_and_reject_spam()

        messages.success(
            request,
            'Dziękujemy za zgłoszenie. Zostanie ono zweryfikowane przez odpowiednie służby.'
        )
        return redirect('cert_detail', cert_id=certificate.certificate_id)

    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')

        batches = Product_batch.objects.filter(certificate_id=certificate)

        return render(request, 'certificates/cert_detail.html', {
            'cert': certificate,
            'batches': batches,
            'fraud_form': form,
            'can_edit': _get_can_edit(request, certificate),
            'form_errors': form.errors,
        })


def show_fraud_report_form(request, certificate_id):
    from ..models import Certificate

    try:
        certificate = Certificate.objects.get(certificate_id=certificate_id)
    except Certificate.DoesNotExist:
        messages.error(request, 'Certyfikat nie istnieje')
        return redirect('main_page')

    batches = Product_batch.objects.filter(certificate_id=certificate)
    form = FraudReportForm()

    return render(request, 'certificates/cert_detail.html', {
        'cert': certificate,
        'batches': batches,
        'fraud_form': form,
        'can_edit': _get_can_edit(request, certificate),
        'show_fraud_modal': True,
    })