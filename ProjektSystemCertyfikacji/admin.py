from django.contrib import admin
from .models import (
    Certyfikat,
    Jednostka_certyfikujaca,
    Jednostka_certyfikat,
    Entity,
    Partia_produktow,
    Weryfikacja_konsumenta,
    Ocena_konsumenta,
    Alert,
    Fraud_report
)

# admin.site.register(Certyfikat)
admin.site.register(Jednostka_certyfikujaca)
admin.site.register(Jednostka_certyfikat)
admin.site.register(Entity)
admin.site.register(Partia_produktow)
admin.site.register(Weryfikacja_konsumenta)
admin.site.register(Ocena_konsumenta)
admin.site.register(Alert)
# admin.site.register(Fraud_report)


@admin.register(Certyfikat)
class CertyfikatAdmin(admin.ModelAdmin):
    readonly_files = ('certificate_url', 'qr_code_img')
    fields = ('certificate_id', 'certificate_number', 'certificate_type', 'holder_entity_id',
              'state', 'valid_from', 'valid_to', 'certificate_hash', 'blockchain_address')
    list_display = ('certificate_id', 'certificate_type', 'certificate_url', 'qr_code_img')

@admin.register(Fraud_report)
class Fraud_report(admin.ModelAdmin):
    fields = ('batch_id', 'certificate_id', 'fraud_type', 'reporter_main', 
              'reporter_email', 'description', 'status' , 'investigation_notes')
    list_display = ('report_id', 'certificate_id', 'status', 'submitted_at')