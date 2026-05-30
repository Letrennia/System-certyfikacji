from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from ProjektSystemCertyfikacji.models import Certificate, Product_batch
from ProjektSystemCertyfikacji.compliance import create_alert

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        updated = Certificate.objects.filter(
            valid_to__lt=today,
            status='valid'
        ).update(status='expired')

        self.stdout.write(f"Zaktualizowano {updated} certyfikatów")

        expiring_soon = Certificate.objects.filter(
            status='valid',
            valid_to__gte=today,
            valid_to__lte=today + timedelta(days=7),
        )
        for cert in expiring_soon:
            create_alert(
                'expiry_warning',
                'medium',
                f"Certyfikat {cert.certificate_number} wygasa {cert.valid_to}.",
            )

        batches_with_expired_cert = Product_batch.objects.filter(
            certificate_id__status='expired',
            status__in=['waiting', 'in_circulation'],
        )
        for batch in batches_with_expired_cert:
            create_alert(
                'batch_issue',
                'high',
                f"Partia '{batch.name}' posiada wygasły certyfikat.",
                batch=batch,
            )