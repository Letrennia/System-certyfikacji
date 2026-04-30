import os
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.utils.html import format_html

from ProjektSystemCertyfikacji.utils.qr_code_generator import generate_qr_code
from main_app import settings
from .models import (
    Certificate,
    Certifying_unit,
    Certifying_unit_certificates,
    Company,
    Product_batch,
    Consumer_verification,
    Consumer_rating,
    Alert,
    Fraud_report as FraudReportModel,
    Chain_event,
    Activity_area,
    Company_activity_area,
    Batch_certificate,
    Notification_cert,
    Certificate_status_history,
    Company_certifying_unit,
    RegistrationCode,
    Producer,
    # encrypt_certificate_id
)

# admin.site.register(Certifying_unit)
# admin.site.register(Certifying_unit_certificates)
# admin.site.register(Company)
# admin.site.register(Product_batch)
# admin.site.register(Consumer_verification)
# admin.site.register(Consumer_rating)
# admin.site.register(Alert)
# admin.site.register(Chain_event)
# admin.site.register(Activity_area)
# admin.site.register(Company_activity_area)
# admin.site.register(Batch_certificate)
# admin.site.register(Notification_cert)
# admin.site.register(Certificate_status_history)
# admin.site.register(Company_certifying_unit)
# admin.site.register(RegistrationCode)
# admin.site.register(Certificate)



@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'name', 'address', 'producer_code')
    list_display = ('producent_id','user', 'name', 'address', 'producer_code', 'is_approved')
    fields = ('user', 'name', 'address', 'producer_code', 'is_approved')

    def save_model(self, request, obj, form, change):
        if obj.is_approved and not obj.user.is_active:
            obj.user.is_active = True
            obj.user.save()
            
        super().save_model(request, obj, form, change)

@admin.register(Certifying_unit_certificates)
class Certifying_unit_certificates_Admin(admin.ModelAdmin):
    list_display = ('jcc_id', 'certifying_unit_id', 'certificate_id')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'name', 'email', 'address', 'country', 'registration_number', 'phone', 'website', 'company_type')
    list_display = ('name', 'company_type', 'country', 'address', 'registration_number', 'is_approved')  
    fields = ('user', 'name', 'email', 'address', 'country', 'registration_number', 'phone', 'website', 'company_type', 'is_approved')

    def save_model(self, request, obj, form, change):
        if obj.is_approved and not obj.user.is_active:
            obj.user.is_active = True
            obj.user.save()
            
        super().save_model(request, obj, form, change) 


@admin.register(Product_batch)
class Product_batch_Admin(admin.ModelAdmin):
    list_display = ('batch_id', 'name', 'category', 'cn_code', 'status')


@admin.register(Consumer_verification)
class Consumer_verification_Admin(admin.ModelAdmin):
    list_display = ('qr_code_scanned', 'consumer_email', 'consumer_ip', 'verification_result', 'batch_id')

    readonly_fields = ('qr_code_scanned', 'consumer_email', 'consumer_ip', 'device_info', 'batch_id')


@admin.register(Consumer_rating)
class Consumer_rating_Admin(admin.ModelAdmin):
    list_display = ('consumer_email', 'rating', 'certificate_id', 'is_verified')

    readonly_fields = ('rating', 'comment', 'consumer_email', 'certificate_id')


@admin.register(Alert)
class Alert_Admin(admin.ModelAdmin):
    list_display = ('alert_id', 'alert_type', 'severity', 'status', 'event_id', 'batch_id')

@admin.register(Chain_event)
class Chain_event(admin.ModelAdmin):
    list_display = ('event_timestamp', 'location', 'batch_id', )


@admin.register(Activity_area)
class Activity_area_Admin(admin.ModelAdmin):
    list_display = ('area_id', 'name')


@admin.register(Company_activity_area)
class Company_activity_area(admin.ModelAdmin):
    list_display = ('cod_id', 'company_id', 'area_id')


@admin.register(Batch_certificate)
class Batch_certificate(admin.ModelAdmin):
    list_display = ('cp_id', 'batch_id', 'certificate_id')


@admin.register(Notification_cert)
class Notification_cert_Admin(admin.ModelAdmin):
    list_display = ('certificate_id', 'notification_type', 'expiry_date', 'sent_to', 'status')


@admin.register(Certificate_status_history)
class Certificate_status_history_Admin(admin.ModelAdmin):
    list_display = ('certificate_id', 'old_status', 'new_status', 'changed_by_user_id', 'changed_date')


@admin.register(Company_certifying_unit)
class Company_certifying_unit_Admin(admin.ModelAdmin):
    list_display = ('ccu_id', 'company_id', 'certifying_unit_id')


@admin.register(RegistrationCode)
class RegistrationCode_Admin(admin.ModelAdmin):
    list_display = ('code', 'is_used', 'created_at')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    readonly_fields = ('qr_code_data', 'qr_code_img')
    list_display = ('certificate_id', 'certificate_number', 'valid_from', 'status', 'qr_code_data', 'qr_code_img')
    fields = ('certificate_number', 'qr_code_data', 'qr_code_img', 'status',
        'valid_from', 'valid_to', 'blockchain_address', 'holder_company_id',
        'issued_by_certifying_unit_id')




@admin.register(Certifying_unit)
class Certifying_unitAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'name', 'address', 'certifying_unit_code')
    list_display = ('certifying_unit_id','user', 'name', 'address', 'certifying_unit_code', 'is_approved')
    fields = ('user', 'name', 'address', 'certifying_unit_code', 'is_approved')

    def save_model(self, request, obj, form, change):
        if obj.is_approved and not obj.user.is_active:
            obj.user.is_active = True
            obj.user.save()
            
        super().save_model(request, obj, form, change)

@admin.register(FraudReportModel)
class FraudReportAdmin(admin.ModelAdmin):
    WHITELIST = [
        'mail@mail.com',
    ]
    BLACKLIST = [
        'spam@mail.com',
    ]

    fields = ('batch_id', 'certificate_id', 'fraud_type',
              'reporter_email', 'description', 'status', 'investigation_notes')
    list_display = ('report_id', 'certificate_id', 'colored_status',
                    'reporter_email_with_count', 'fraud_type')
    list_filter = ('status', 'fraud_type')
    search_fields = ('reporter_email', 'description')
    ordering = ('status',)
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
        three_minutes_ago = timezone.now() - timedelta(minutes=3)
        recent_reports = FraudReportModel.objects.filter(
            reporter_email=current_report.reporter_email,
            status='new',
            created_at__gte=three_minutes_ago
        )
        unique_certificates = recent_reports.values('certificate_id').distinct().count()
        if unique_certificates >= 3:
            spam_reports = recent_reports.filter(status='new')
            spam_reports.update(
                status='rejected',
                investigation_notes='WYKRYTO SPAM (3+ zgłoszenia z różnych certyfikatów w ciągu 3 minut)'
            )

            if current_report.reporter_email not in self.BLACKLIST:
                self.BLACKLIST.append(current_report.reporter_email)

            self.message_user(
                request,
                f'Wykryto spam od {current_report.reporter_email}. '
                f'Automatycznie odrzucono {spam_reports.count()} zgłoszeń.',
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