from django.core.management.base import BaseCommand
from django.utils import timezone
from ProjektSystemCertyfikacji.models import Certificate

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        updated = Certificate.objects.filter(
            valid_to__lt=today,
            status='valid'
        ).update(status='expired')

        self.stdout.write(f"Zaktualizowano {updated} certyfikatów")