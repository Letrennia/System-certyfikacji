from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Certificate, Certificate_status_history, Certifying_unit
from django.utils import timezone

@receiver(pre_save, sender=Certificate)
def log_certificate_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Certificate.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Znajdź kto zmienił status (z sesji lub requestu)
                # To jest uproszczone - w prawdziwej aplikacji przekaż użytkownika z requestu
                from django.contrib.sessions.models import Session
                
                # Dla uproszczenia - używamy domyślnej jednostki certyfikującej
                # W rzeczywistej implementacji przekaż użytkownika przez dodatkowy parametr
                try:
                    certifying_unit = Certifying_unit.objects.first()  # Tymczasowe
                except:
                    certifying_unit = None
                
                # Zapisz historię zmian
                Certificate_status_history.objects.create(
                    certificate_id=instance,
                    old_status=old_instance.status,
                    new_status=instance.status,
                    changed_by_user_id=certifying_unit,
                    reason=f"Automatyczna zmiana statusu z {old_instance.get_status_display()} na {instance.get_status_display()}"
                )
        except Certificate.DoesNotExist:
            pass