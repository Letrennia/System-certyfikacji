from datetime import timedelta
from django.utils import timezone
import os
from django.db import models
from django.contrib.auth.models import User

from cryptography.fernet import Fernet
import base64
from django.conf import settings

from ProjektSystemCertyfikacji.utils.qr_code_generator import generate_qr_code
from main_app import settings


def encrypt_certificate_id(certificate_id):
    f = Fernet(settings.FERNET_KEY)
    token = f.encrypt(str(certificate_id).encode())
    return base64.urlsafe_b64encode(token).decode().rstrip('=')


class Company(models.Model):
    company_id = models.AutoField(primary_key=True, db_column='company_id')
    company_type = models.CharField(max_length=50, null=False, db_column='company_type')
    name = models.CharField(max_length=200, null=False, db_column='name')
    email = models.CharField(max_length=100, db_column='email')
    address = models.CharField(max_length=500, db_column='address')
    country = models.CharField(max_length=100, default='Poland', db_column='country')
    registration_number = models.CharField(max_length=50, db_column='registration_number')
    phone = models.CharField(max_length=20, db_column='phone')
    website = models.CharField(max_length=255, db_column='website')
    blockchain_address = models.CharField(max_length=255, db_column='blockchain_address')

    class Meta:
        db_table = 'company'
        # managed = False


class Activity_area(models.Model):
    area_id = models.AutoField(primary_key=True, db_column='area_id')
    name = models.CharField(max_length=100, unique=True, null=False, db_column='name')
    description = models.CharField(max_length=1000, db_column='description')

    class Meta:
        db_table = 'activity_area'
        # managed = False


class Certifying_unit(models.Model):
    certifying_unit_id = models.AutoField(primary_key=True, db_column='certifying_unit_id')    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='certifying_unit')
    name = models.CharField(max_length=200, null=False, db_column='name')
    address = models.CharField(max_length=500, db_column='address')
    certifying_unit_code = models.CharField(max_length=50, unique=True, null=False, db_column='certifying_unit_code')
    is_approved = models.BooleanField(default=False, db_column='is_approved')
    # username = models.CharField(max_length=100, unique=True, null=False, db_column='username')
    # password = models.CharField(max_length=255, null=False, db_column='password')
    # email = models.CharField(max_length=100, unique=True, null=False)

    class Meta:
        db_table = 'certifying_unit'
        # manage = False

    def __str__(self):
        return self.name


class Company_activity_area(models.Model):
    cod_id = models.AutoField(primary_key=True, db_column='cod_id')

    company_id = models.ForeignKey('Company', on_delete=models.DO_NOTHING, db_column='company_id')
    area_id = models.ForeignKey('Activity_area', on_delete=models.DO_NOTHING, db_column='area_id')

    class Meta:
        db_table = 'company_activity_area'
        # manage = False


class Certificate(models.Model):
    certificate_id = models.AutoField(primary_key=True, db_column='certificate_id')
    certificate_number = models.CharField(max_length=50, unique=True, null=False, db_column='certificate_number')
    certificate_type = models.CharField(max_length=50, null=False, db_column='certificate_type')
    certificate_publisher = models.CharField(max_length=200, db_column='certificate_publisher')
    STATUS = [
        ('none', 'None'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('pending', 'Pending')
    ]
    status = models.CharField(max_length=50, choices=STATUS, default='valid', db_column='status')
    qr_code_data = models.CharField(max_length=500, db_column='qr_code_data')  # Podmieniono z certificate_url
    valid_from = models.DateField(null=False, db_column='valid_from')
    valid_to = models.DateField(null=False, db_column='valid_to')
    blockchain_address = models.CharField(max_length=255, blank=True, null=True)
    holder_company_id = models.ForeignKey('Company', on_delete=models.DO_NOTHING, db_column='holder_company_id')
    issued_by_certifying_unit_id = models.ForeignKey('Certifying_unit', on_delete=models.DO_NOTHING,
                                                     db_column='issued_by_certifying_unit_id')

    qr_code_img = models.ImageField(upload_to='qr_codes/', blank=True,
                                    null=True)  # Dodane w celu przetrzymywania img qr kodów

    class Meta:
        db_table = 'certificate'
        # manage = False

    def get_certificate_url(self):
        from django.urls import reverse
        return reverse('certificate_detail', args=[self.certificate_id])

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if created or not self.qr_code_data:
            encrypt_id = encrypt_certificate_id(self.certificate_id)
            self.qr_code_data = f"http://127.0.0.1:8000/certificate/{encrypt_id}/"

            qr_path = os.path.join(settings.MEDIA_ROOT, f'qr_codes/certificate_{self.certificate_id}.png')
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            generate_qr_code(self.qr_code_data, qr_path)

            self.qr_code_img.name = f'qr_codes/certificate_{self.certificate_id}.png'
            super().save(update_fields=['qr_code_data', 'qr_code_img'])


class Certifying_unit_certificates(models.Model):
    jcc_id = models.AutoField(primary_key=True, db_column='jcc_id')

    certifying_unit_id = models.ForeignKey('Certifying_unit', on_delete=models.DO_NOTHING,
                                           db_column='certifying_unit_id')
    certificate_id = models.ForeignKey('Certificate', on_delete=models.DO_NOTHING, db_column='certificate_id')

    class Meta:
        db_table = 'certifying_unit_certificates'
        # manage = False


class Product_batch(models.Model):
    batch_id = models.AutoField(primary_key=True, db_column='batch_id')
    category = models.CharField(max_length=100, db_column='category')
    name = models.CharField(max_length=200, null=False, db_column='name')
    cn_code = models.CharField(max_length=20, db_column='cn_code')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False, db_column='quantity')
    UNIT = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Liter'),
        ('ml', 'Miligram'),
        ('p', 'Pieces')
    ]
    unit_of_measure = models.CharField(max_length=20, choices=UNIT, db_column='unit_of_measure')
    blockchain_hash = models.CharField(max_length=255, db_column='blockchain_hash')
    status = models.CharField(max_length=50, default='waiting', db_column='status')
    storage_conditions = models.CharField(max_length=500, null=False, db_column='storage_conditions')
    transport_temperature = models.DecimalField(max_digits=6, decimal_places=2, null=False,
                                                db_column='transport_temperature')
    harvest_date = models.DateField(null=True, blank=True, db_column='harvest_date')
    production_date = models.DateField(null=False, db_column='production_date')
    expiration_date = models.DateField(null=False, db_column='expiration_date')

    certificate_id = models.ForeignKey('Certificate', on_delete=models.DO_NOTHING, db_column='certificate_id')
    certifying_unit_id = models.ForeignKey('Certifying_unit', on_delete=models.DO_NOTHING,
                                           db_column='certifying_unit_id')

    class Meta:
        db_table = 'product_batch'
        # manage = False


class Chain_event(models.Model):
    event_id = models.AutoField(primary_key=True, db_column='event_id')
    event_timestamp = models.DateTimeField(auto_now_add=True, db_column='event_timestamp')
    location = models.CharField(max_length=255, db_column='location')
    blockchain_hash = models.CharField(max_length=255, db_column='blockchain_hash')
    blockchain_tx_id = models.CharField(max_length=255, db_column='blockchain_tx_id')

    batch_id = models.ForeignKey('Product_batch', on_delete=models.DO_NOTHING, db_column='batch_id')
    area_id = models.ForeignKey('Activity_area', on_delete=models.DO_NOTHING, db_column='area_id')
    company_id = models.ForeignKey('Company', on_delete=models.DO_NOTHING, db_column='company_id')
    certificate_id = models.ForeignKey('Certificate', on_delete=models.DO_NOTHING, db_column='certificate_id')

    class Meta:
        db_table = 'chain_event'
        # manage = False


class Batch_certificate(models.Model):
    cp_id = models.AutoField(primary_key=True, db_column='cp_id')

    batch_id = models.ForeignKey('Product_batch', on_delete=models.DO_NOTHING, db_column='batch_id')
    certificate_id = models.ForeignKey('Certificate', on_delete=models.DO_NOTHING, db_column='certificate_id')

    class Meta:
        db_table = 'batch_certificate'
        # manage = False


class Alert(models.Model):
    alert_id = models.AutoField(primary_key=True, db_column='alert_id')
    alert_type = models.CharField(max_length=100, db_column='alert_type')
    description = models.CharField(max_length=1000, db_column='description')
    severity = models.CharField(max_length=50, db_column='severity')
    STATUS = [
        ('done', 'Done'),
        ('new', 'New')
    ]
    status = models.CharField(max_length=50, choices=STATUS, default='new', db_column='status')

    event_id = models.ForeignKey('Chain_event', on_delete=models.DO_NOTHING, db_column='event_id', default=1)
    batch_id = models.ForeignKey('Product_batch', on_delete=models.DO_NOTHING, db_column='batch_id')

    class Meta:
        db_table = 'alert'
        # manage = False


class Consumer_verification(models.Model):
    verification_id = models.AutoField(primary_key=True, db_column='verification_id')
    qr_code_scanned = models.CharField(max_length=500, db_column='qr_code_scanned')
    verification_result = models.CharField(max_length=50, db_column='verification_result')
    consumer_email = models.CharField(max_length=100, db_column='consumer_email')
    consumer_ip = models.CharField(max_length=45, db_column='consumer_ip')
    device_info = models.CharField(max_length=255, db_column='device_info')

    batch_id = models.ForeignKey('Product_batch', on_delete=models.DO_NOTHING, db_column='batch_id')

    class Meta:
        db_table = 'consumer_verification'
        # managed = False


class Consumer_rating(models.Model):
    rating_id = models.AutoField(primary_key=True, db_column='rating_id')
    rating = models.IntegerField(null=True, db_column='rating')
    comment = models.CharField(max_length=1000, db_column='comment')
    consumer_email = models.CharField(max_length=100, db_column='consumer_email')
    is_verified = models.IntegerField(default=0, null=False, db_column='is_verified')

    certificate_id = models.ForeignKey('Certificate', on_delete=models.DO_NOTHING, db_column='certificate_id')

    class Meta:
        db_table = 'consumer_rating'
        # managed = False


class Notification_cert(models.Model):
    notification_id = models.AutoField(primary_key=True, db_column='notification_id')
    notification_type = models.CharField(max_length=50, db_column='notification_type')
    expiry_date = models.DateField(null=True, blank=True, db_column='expiry_date')
    sent_to = models.CharField(max_length=100, db_column='sent_to')
    status = models.CharField(max_length=50, default='unsent', db_column='status')

    certificate_id = models.ForeignKey('Certificate', on_delete=models.DO_NOTHING, db_column='certificate_id')

    class Meta:
        db_table = 'notification_cert'
        # managed = False


class Fraud_report(models.Model):
    report_id = models.AutoField(primary_key=True, db_column='report_id')
    TYPE = [
        ('fake_id', "Fake ID"),
        ('fake_cert_id', "Fake certification ID"),
        ('other', 'Other')
    ]
    fraud_type = models.CharField(max_length=100, choices=TYPE, db_column='fraud_type')
    reporter_email = models.CharField(max_length=100, db_column='reporter_email')
    description = models.CharField(max_length=1000, db_column='description')
    STATUS = [
        ('new', 'New'),
        ('investigating', 'Investigation'),
        ('rejected', 'Rejected')
    ]
    status = models.CharField(max_length=50, choices=STATUS, default='new', db_column='status')
    investigation_notes = models.CharField(max_length=1000, db_column='investigation_notes')

    batch_id = models.ForeignKey('Product_batch', on_delete=models.DO_NOTHING, db_column='batch_id')
    certificate_id = models.ForeignKey('Certificate', on_delete=models.DO_NOTHING, db_column='certificate_id')
    created_at = models.DateTimeField(auto_now_add=True)

    def check_and_reject_spam(self):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_reports = Fraud_report.objects.filter(
            reporter_email=self.reporter_email,
            status='new',
            created_at__gte=one_hour_ago
        )
        unique_certificates = recent_reports.values('certificate_id').distinct().count()
        if unique_certificates >= 3:
            spam_reports = recent_reports.filter(status='new')
            spam_reports.update(
                status='rejected',
                investigation_notes='WYKRYTO SPAM (3+ zgłoszenia z różnych certyfikatów w ciągu godziny)'
            )
            return True
        return False

    class Meta:
        db_table = 'fraud_reports'
        # managed = False


class Certificate_status_history(models.Model):
    history_id = models.AutoField(primary_key=True, db_column='history_id')
    old_status = models.CharField(max_length=50, db_column='old_status')
    new_status = models.CharField(max_length=50, null=False, db_column='new_status')
    changed_by_user_id = models.IntegerField(null=False, db_column='changed_by_user_id')
    changed_date = models.DateTimeField(auto_now_add=True, db_column='changed_date')

    reason = models.CharField(max_length=1000, db_column='reason')

    certificate_id = models.ForeignKey('Certificate', on_delete=models.DO_NOTHING, db_column='certificate_id')

    class Meta:
        db_table = 'certificate_status_history'
        # managed = False


class Company_certifying_unit(models.Model):
    ccu_id = models.AutoField(primary_key=True, db_column='ccu_id')

    company_id = models.ForeignKey('Company', on_delete=models.DO_NOTHING, db_column='company_id')
    certifying_unit_id = models.ForeignKey('Certifying_unit', on_delete=models.DO_NOTHING,
                                           db_column='certifying_unit_id')

    class Meta:
        db_table = 'company_certifying_unit'
        # managed = False
        unique_together = ('company_id', 'certifying_unit_id')



# do generowania kodu walidacji jednostki certyfikujacej

class RegistrationCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registration_code'

    def __str__(self):
        return self.code