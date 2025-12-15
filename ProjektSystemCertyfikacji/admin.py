from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.utils.html import format_html
from .models import (
    Certyfikat,
    Jednostka_certyfikujaca,
    Jednostka_certyfikat,
    Entity,
    Partia_produktow,
    Weryfikacja_konsumenta,
    Ocena_konsumenta,
    Alert,
    Fraud_report as FraudReportModel
)

admin.site.register(Jednostka_certyfikujaca)
admin.site.register(Jednostka_certyfikat)
admin.site.register(Entity)
admin.site.register(Partia_produktow)
admin.site.register(Weryfikacja_konsumenta)
admin.site.register(Ocena_konsumenta)
admin.site.register(Alert)


@admin.register(Certyfikat)
class CertyfikatAdmin(admin.ModelAdmin):
    readonly_fields = ('certificate_url', 'qr_code_img')
    fields = ('certificate_id', 'certificate_number', 'certificate_type', 'holder_entity_id',
              'state', 'valid_from', 'valid_to', 'certificate_hash', 'blockchain_address')
    list_display = ('certificate_id', 'certificate_type', 'certificate_url', 'qr_code_img')


@admin.register(FraudReportModel)
class FraudReportAdmin(admin.ModelAdmin):
    WHITELIST = [
        'mail@mail.com',
    ]
    BLACKLIST = [
        'spam@mail.com',
    ]

    fields = ('batch_id', 'certificate_id', 'fraud_type', 'reporter_main',
              'reporter_email', 'description', 'status', 'investigation_notes')
    list_display = ('report_id', 'certificate_id', 'colored_status', 'submitted_at',
                    'reporter_email_with_count', 'fraud_type')
    list_filter = ('status', 'fraud_type', 'submitted_at')
    search_fields = ('reporter_email', 'reporter_main', 'description')
    ordering = ('status', '-submitted_at')
    actions = ['mark_as_investigating', 'mark_as_rejected', 'mark_as_new']

    @admin.action(description='Oznacz jako "W toku"')
    def mark_as_investigating(self, request, queryset):
        updated = queryset.update(status='investigating')
        self.message_user(request, f'Zmieniono status {updated} zgłoszeń na "W toku".')

    @admin.action(description='Oznacz jako "Odrzucony"')
    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'Odrzucono {updated} zgłoszeń.')

    @admin.action(description='Oznacz jako "Nowy"')
    def mark_as_new(self, request, queryset):
        updated = queryset.update(status='new')
        self.message_user(request, f'Zmieniono status {updated} zgłoszeń na "Nowy".')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            reporter_count=Count('reporter_email')
        )
        return qs

    def reporter_email_with_count(self, obj):
        total_reports = FraudReportModel.objects.filter(
            reporter_email=obj.reporter_email
        ).count()
        badge = ''
        if obj.reporter_email in self.WHITELIST:
            badge = ' <span style="background:#4caf50;color:white;padding:2px 6px;border-radius:3px;font-size:10px;">✓ WHITELIST</span>'
        elif obj.reporter_email in self.BLACKLIST:
            badge = ' <span style="background:#f44336;color:white;padding:2px 6px;border-radius:3px;font-size:10px;">✗ BLACKLIST</span>'
        return format_html(
            '{} <span style="color:#666;font-size:11px;">({})</span>{}',
            obj.reporter_email,
            total_reports,
            badge
        )
    reporter_email_with_count.short_description = 'Email zgłaszającego'
    reporter_email_with_count.admin_order_field = 'reporter_email'

    def colored_status(self, obj):
        colors = {
            'new': '#2196f3',
            'investigating': '#ff9800',
            'rejected': '#f44336'
        }
        color = colors.get(obj.status, '#666')
        status_display = dict(FraudReportModel.STATUS).get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:4px 8px;border-radius:3px;font-weight:bold;">{}</span>',
            color,
            status_display
        )
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'

    def get_list_display_links(self, request, list_display):
        return ('report_id',)

    def save_model(self, request, obj, form, change):
        if obj.reporter_email in self.BLACKLIST:
            obj.status = 'rejected'
            obj.investigation_notes = 'ODRZUCONO - email znajduje się na blackliście'
            super().save_model(request, obj, form, change)
            self.message_user(
                request,
                f'Zgłoszenie od {obj.reporter_email} automatycznie odrzucone (BLACKLIST)',
                level='warning'
            )
            return
        super().save_model(request, obj, form, change)
        if obj.status == 'new' and obj.reporter_email not in self.WHITELIST:
            self._check_and_reject_spam(obj, request)

    def _check_and_reject_spam(self, current_report, request):
        time_threshold = timezone.now() - timedelta(hours=1)
        recent_reports = FraudReportModel.objects.filter(
            reporter_email=current_report.reporter_email,
            submitted_at__gte=time_threshold
        )
        unique_certificates = recent_reports.values('certificate_id').distinct().count()
        if unique_certificates >= 3:
            spam_reports = recent_reports.filter(status='new')
            spam_reports.update(
                status='rejected',
                investigation_notes='WYKRYTO SPAM(3+ zgłoszenia z różnych certyfikatów w ciągu godziny)'
            )
            self.message_user(
                request,
                f'Wykryto spam od {current_report.reporter_email}. '
                f'Automatycznie odrzucono {spam_reports.count()} zgłoszeń. ',
                level='warning'
            )

    def changelist_view(self, request, extra_context=None):
        """
        Dodano statystyki
        """
        extra_context = extra_context or {}
        total = FraudReportModel.objects.count()
        new = FraudReportModel.objects.filter(status='new').count()
        investigating = FraudReportModel.objects.filter(status='investigating').count()
        rejected = FraudReportModel.objects.filter(status='rejected').count()
        extra_context['fraud_stats'] = {
            'total': total,
            'new': new,
            'investigating': investigating,
            'rejected': rejected
        }
        return super().changelist_view(request, extra_context)