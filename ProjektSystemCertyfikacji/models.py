import os
from django.db import models

from ProjektSystemCertyfikacji.utils.qr_code_generator import generate_qr_code
from main_app import settings


class Certyfikat(models.Model):
    certificate_id = models.CharField(max_length=20, primary_key=True)
    certificate_number = models.CharField(max_length=20)  # to trzeba sprawdzic ile mam makysmalnie znakow
    TYPE = [
        ('inne', 'Inne'),
        ('produkcja', 'Produkcja')
    ]
    certificate_type = models.CharField(max_length=20, choices=TYPE, default='inne')
    # nie ma id_jednostki poniewaz jeżeli mamy miec (tak jak jest na diagramie) tabele pomocniczą to umieszczenie tutaj tego id nie ma sensu
    holder_entity_id = models.IntegerField()  # ?
    STATE = [
        ('none', 'None'),
        ('wazny', 'Wazny'),
        ('wygasly', 'Wygasly'),
        ('uniewazniony', 'Uniewazniony'),
        ('oczekujacy', 'Oczekujacy')
    ]
    state = models.CharField(max_length=15, choices=STATE, default='none')
    valid_from = models.DateField()
    valid_to = models.DateField()
    # certificate_publisher ?
    # qr_code_data = models.TextField(blank=True, null=True)  # Placeholder
    certificate_hash = models.CharField(max_length=100)
    blockchain_address = models.CharField(max_length=100)
    certificate_url = models.URLField(blank=True, null=True)
    qr_code_img = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def get_certificate_url(self):
        from django.urls import reverse
        return reverse('certificate_detail', args=[self.certificate_id])
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        #poxniej do zmiany
        self.certificate_url = f"http://127.0.0.1:8000{self.get_certificate_url()}"
        qr_path = os.path.join(settings.MEDIA_ROOT, f'qr_codes/certificate_{self.certificate_id}.png')
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        generate_qr_code(self.certificate_url, qr_path)

        self.qr_code_img.name = f'qr_codes/certificate_{self.certificate_id}.png'
        super().save(update_fields=['certificate_url','qr_code_img'])     


class Jednostka_certyfikujaca(models.Model):
    authority_id = models.AutoField(primary_key=True)
    authority_name = models.CharField(max_length=30)
    authority_address = models.TextField()
    authority_ODU = models.CharField(max_length=30)  # ODU - Organizational Unit Number
    establishment_date = models.DateField()


class Jednostka_certyfikat(models.Model):
    authority_id = models.ForeignKey(
        Jednostka_certyfikujaca,
        on_delete=models.CASCADE
    )
    certificate_id = models.ForeignKey(
        Certyfikat,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('authority_id', 'certificate_id')


class Entity(models.Model):
    entity_id = models.AutoField(primary_key=True)
    entity_type = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=100, unique=True)
    address = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=15)
    blockchain_address = models.CharField(max_length=40)
    is_active = models.BooleanField(default=False)
    AREA = [
        ('prodction', "Produkcja"),
        ('storage', "Przechowywanie"),
        ('distribution', "Dystrybucja"),
        ('import', "Import"),
        ('export', "Eksport")

    ]
    area_of_activity = models.TextField(max_length=30, choices=AREA)


class Partia_produktow(models.Model):
    batch_id = models.AutoField(primary_key=True)
    certificate_id = models.ForeignKey(
        Certyfikat,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=20)
    CATEGORY = [
        ('inne', 'Inne'),
        ('warzywa', 'Warzywa'),
        ('owoce', 'Owoce'),
        ('nabial', 'Nabial'),
        ('mieso', 'Mieso')
    ]
    category = models.CharField(max_length=20, choices=CATEGORY, default='inne')
    codeCN = models.CharField(max_length=8)
    production_date = models.DateField()
    producer_id = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE
    )
    expiration_date = models.DateField()
    amount = models.IntegerField()
    UNIT = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Litr'),
        ('ml', 'Miligram'),
        ('szt', 'Sztuki')
    ]
    unit = models.CharField(max_length=10, choices=UNIT, default='szt')
    # qr_code_data = models.TextField(blank=True, null=True)  # Placeholder
    blockchain_hash = models.CharField(max_length=64, unique=True)  # ?


class Weryfikacja_konsumenta(models.Model):
    verification_id = models.CharField(max_length=20, primary_key=True)
    batch_id = models.ForeignKey(
        Partia_produktow,
        on_delete=models.CASCADE,
    )
    qr_code_scanned = models.CharField(max_length=255)
    verification_result = models.BooleanField()
    scanned_at = models.DateTimeField(auto_now_add=True)


class Ocena_konsumenta(models.Model):
    rating_id = models.CharField(max_length=20, primary_key=True)
    batch_id = models.ForeignKey(
        Partia_produktow,
        on_delete=models.CASCADE,
    )
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


class Alert(models.Model):
    alert_id = models.AutoField(primary_key=True)
    TYPE = [
        ('none', "None"),
        ('error', 'Blad'),
        ('warning', 'Ostrzezenie')
    ]
    alert_type = models.CharField(max_length=10, choices=TYPE, default='none')
    SEVERITY = [
        ('niski', 'Niski'),
        ('krytyczny', 'Krytyczny')
    ]
    alert_severity = models.CharField(max_length=10, choices=SEVERITY, default='niski')
    STATE = [
        ('none', 'None'),
        ('wykonane', 'Wykonane')
    ]
    alert_state = models.CharField(max_length=10, choices=STATE, default='none')
    certificate_id = models.ForeignKey(
        Certyfikat,
        on_delete=models.CASCADE
    )
    batch_id = models.ForeignKey(
        Partia_produktow,
        on_delete=models.CASCADE
    )
    event_id = models.TextField(blank=True, null=True)  # Placeholder
    description = models.TextField(max_length=255)


class Fraud_report(models.Model):
    report_id = models.AutoField(primary_key=True)
    batch_id = models.ForeignKey(
        Partia_produktow,
        on_delete=models.CASCADE
    )
    certificate_id = models.ForeignKey(
        Certyfikat,
        on_delete=models.CASCADE
    )
    TYPE = [
        ('fake_id', "Fake ID"),
        ('fake_cert_id', "Fake certification ID")
    ]
    fraud_type = models.CharField(max_length=20, choices=TYPE)
    reporter_main = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    STATE = [
        ('new', 'Nowy'),
        ('investigating', 'W toku'),
        ('rejected', 'Odrzucony')
    ]
    report_state = models.CharField(max_length=20, choices=STATE)
    submitted_at = models.DateTimeField(auto_now_add=True)