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

admin.site.register(Certyfikat)
admin.site.register(Jednostka_certyfikujaca)
admin.site.register(Jednostka_certyfikat)
admin.site.register(Entity)
admin.site.register(Partia_produktow)
admin.site.register(Weryfikacja_konsumenta)
admin.site.register(Ocena_konsumenta)
admin.site.register(Alert)
admin.site.register(Fraud_report)