from datetime import timedelta
from urllib import request
from django.urls import reverse
from django.utils import timezone
import os
from django.db import models
from django.contrib.auth.models import User

from django.core.validators import MinValueValidator, MaxValueValidator

from cryptography.fernet import Fernet
import base64
from django.conf import settings

from ProjektSystemCertyfikacji.utils.qr_code_generator import generate_qr_code
from main_app import settings
import qrcode
from ProjektSystemCertyfikacji.utils.local_ip import get_local_ip


def encrypt_certificate_id(certificate_id):
    f = Fernet(settings.FERNET_KEY)
    token = f.encrypt(str(certificate_id).encode())
    return base64.urlsafe_b64encode(token).decode().rstrip('=')


def decrypt_certificate_id(token_str):
    f = Fernet(settings.FERNET_KEY)

    padding = '=' * (-len(token_str) % 4)
    token_bytes = base64.urlsafe_b64decode(token_str + padding)

    decrypted_bytes = f.decrypt(token_bytes)
    return int(decrypted_bytes.decode())


class Company(models.Model):
    company_id = models.AutoField(primary_key=True, db_column='company_id')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_user', null=False)
    COMPANY_TYPE = [
        ('producer', 'Producent'),
        ('distributor', 'Dystrybutor'),
        # ('certifier', 'Certyfikator'),
        ('warehouse', 'Magazyn'),
        ('import', 'Import'),
        ('export', 'Export'),
    ]
    company_type = models.CharField(max_length=50, choices=COMPANY_TYPE, null=False, db_column='company_type')
    name = models.CharField(max_length=200, null=False, db_column='name')
    email = models.CharField(max_length=100, db_column='email')
    address = models.CharField(max_length=500, db_column='address')
    country = models.CharField(max_length=100, default='Poland', db_column='country')
    registration_number = models.CharField(max_length=50, db_column='registration_number')
    phone = models.CharField(max_length=20, db_column='phone')
    website = models.CharField(max_length=255, db_column='website')
    blockchain_address = models.CharField(max_length=255, db_column='blockchain_address')
    is_approved = models.BooleanField(default=False, db_column='is_approved', null=True)

    class Meta:
        db_table = 'company'
        # managed = False
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'



    def __str__(self):
        return self.name


class Activity_area(models.Model):
    area_id = models.AutoField(primary_key=True, db_column='area_id')
    
    ACTIVITY_CHOICES = [
        ('production', 'Produkcja'),
        ('preparation', 'Przygotowywanie'),
        ('distribution', 'Distribution'), # Dodane w ten sposób, ponieważ tak wygląda to w oryginale
        ('introduction', 'Dystrybucja/Wprowadzanie do obrotu'),
        ('storage', 'Przechowywanie'),
        ('import', 'Import'),
        ('export', 'Eksport'),
    ]
    
    name = models.CharField(max_length=100, unique=True, null=False, choices=ACTIVITY_CHOICES, db_column='name')
    description = models.CharField(max_length=1000, db_column='description')
    
    class Meta:
        db_table = 'activity_area'
        verbose_name = 'Activity area'
        verbose_name_plural = 'Activity areas'
    
    def __str__(self):
        return self.get_name_display()


class Certifying_unit(models.Model):
    certifying_unit_id = models.AutoField(primary_key=True, db_column='certifying_unit_id')    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='certifying_unit')
    name = models.CharField(max_length=200, null=False, db_column='name')
    address = models.CharField(max_length=500, db_column='address')
    certifying_unit_code = models.CharField(max_length=50, unique=True, null=False, db_column='certifying_unit_code')
    is_approved = models.BooleanField(default=False, db_column='is_approved')
    
    class Meta:
        db_table = 'certifying_unit'
        # manage = False
        verbose_name = 'Certifying unit'
        verbose_name_plural = 'Certifying units'

    def __str__(self):
        return self.name


class Company_activity_area(models.Model):
    cod_id = models.AutoField(primary_key=True, db_column='cod_id')

    company_id = models.ForeignKey('Company', on_delete=models.CASCADE, db_column='company_id')
    area_id = models.ForeignKey('Activity_area', on_delete=models.CASCADE, db_column='area_id')

    class Meta:
        db_table = 'company_activity_area'
        # manage = False
        verbose_name = 'Company activity area'
        verbose_name_plural = 'Company activity areas'

    def __str__(self):
        return f"{self.cod_id} | {self.company_id} | {self.area_id}"


class Certificate(models.Model):
    certificate_id = models.AutoField(primary_key=True, db_column='certificate_id')
    certificate_number = models.CharField(max_length=50, unique=True, null=False, db_column='certificate_number')
    SUBJECT_TYPE_CHOICES = [
        ('group_of_subjects', 'Grupa podmiotów'),
        ('subject', 'Podmiot'),
        ]
    #certificate_type = models.CharField(max_length=50, null=False, db_column='certificate_type')
    subject_type = models.CharField(
        max_length=50,
        choices=SUBJECT_TYPE_CHOICES,
        default='subject',
        null=False,
        db_column='subject_type'
        )

    #certificate_publisher = models.CharField(max_length=200, db_column='certificate_publisher')
    STATUS = [
        #('none', 'None'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('pending', 'Pending')
    ]
    status = models.CharField(max_length=50, choices=STATUS, default='valid', db_column='status')
    qr_code_data = models.CharField(max_length=500, db_column='qr_code_data')  # Podmieniono z certificate_url
    valid_from = models.DateField(null=False, db_column='valid_from')
    valid_to = models.DateField(null=False, db_column='valid_to')
    activity_areas = models.ManyToManyField(
        Activity_area,
        related_name='certificates',
        blank=True,
        help_text="Wybierz obszary działalności"
    )
    blockchain_address = models.CharField(max_length=255, blank=True, null=True)
    holder_company_id = models.ForeignKey('Company', on_delete=models.CASCADE, db_column='holder_company_id')
    issued_by_certifying_unit_id = models.ForeignKey('Certifying_unit', on_delete=models.PROTECT,
                                                     db_column='issued_by_certifying_unit_id')

    qr_code_img = models.ImageField(upload_to='qr_codes/', blank=True,
                                    null=True)  # Dodane w celu przetrzymywania img qr kodów

    pdf_file = models.FileField(upload_to='certificate_files/', blank=True,
                                null=True) # Dodane do przechowywania oryginalnych certyfikatów

    class Meta:
        db_table = 'certificate'
        # manage = False

    def get_app_host(self):
        if hasattr(settings, 'APP_HOST'):
            return settings.APP_HOST
        ip = get_local_ip()
        return f"http://{ip}:8000"
    

    def generate_qr(self):
        encrypt_id = encrypt_certificate_id(self.certificate_id)
        self.qr_code_data = encrypt_id

        qr_url = f"/redirect/{encrypt_id}/"

        qr_path = os.path.join(
            settings.MEDIA_ROOT,
            f'qr_codes/certificate_{self.certificate_id}.png'
        )
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)

        generate_qr_code(qr_url, qr_path)

        self.qr_code_img.name = f'qr_codes/certificate_{self.certificate_id}.png'



    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self.generate_qr()
            super().save(update_fields=['qr_code_data', 'qr_code_img'])

    def __str__(self):
        return self.certificate_number


class Certifying_unit_certificates(models.Model):
    jcc_id = models.AutoField(primary_key=True, db_column='jcc_id')

    certifying_unit_id = models.ForeignKey('Certifying_unit', on_delete=models.CASCADE,
                                           db_column='certifying_unit_id')
    certificate_id = models.ForeignKey('Certificate', on_delete=models.CASCADE, db_column='certificate_id')

    class Meta:
        db_table = 'certifying_unit_certificates'
        # manage = False

        verbose_name = 'Certifying unit certificate'
        verbose_name_plural = 'Certifying unit certificates'


    # def __str__(self):
    #     return f"{self.certifying_unit_id} → {self.certificate_id}"


class Product_batch(models.Model):
    batch_id = models.AutoField(primary_key=True, db_column='batch_id')
    category = models.CharField(max_length=100, db_column='category')
    name = models.CharField(max_length=200, null=False, db_column='name')
    cn_code = models.CharField(max_length=20, db_column='cn_code')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False, db_column='quantity')
    UNIT = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Litr'),
        ('ml', 'Miligram'),
        ('p', 'Sztuk')
    ]
    unit_of_measure = models.CharField(max_length=20, choices=UNIT, db_column='unit_of_measure')
    blockchain_hash = models.CharField(max_length=255, db_column='blockchain_hash')
    
    STATUS = [
    ('waiting', 'Oczekujące'),
    ('in_circulation', 'W obiegu'),
    ('delivered', 'Dostarczone'),
    ('recalled', 'Wycofane'),
]
    status = models.CharField(max_length=50,choices=STATUS, default='waiting', db_column='status')
    storage_conditions = models.CharField(max_length=500, null=False, db_column='storage_conditions')
    transport_temperature = models.DecimalField(max_digits=6, decimal_places=2, null=False,
                                                db_column='transport_temperature')
    harvest_date = models.DateField(null=True, blank=True, db_column='harvest_date')
    production_date = models.DateField(null=False, db_column='production_date')
    expiration_date = models.DateField(null=False, db_column='expiration_date')

    certificate_id = models.ForeignKey('Certificate', on_delete=models.PROTECT, db_column='certificate_id')
    certifying_unit_id = models.ForeignKey('Certifying_unit', on_delete=models.CASCADE,
                                           db_column='certifying_unit_id')

    class Meta:
        db_table = 'product_batch'
        # manage = False
        verbose_name = 'Product batch'
        verbose_name_plural = 'Product batches'

    def __str__(self):
        return self.name


class Chain_event(models.Model):
    event_id = models.AutoField(primary_key=True, db_column='event_id')
    event_timestamp = models.DateTimeField(auto_now_add=True, db_column='event_timestamp')
    location = models.CharField(max_length=255, db_column='location')
    blockchain_hash = models.CharField(max_length=255, db_column='blockchain_hash')
    blockchain_tx_id = models.CharField(max_length=255, db_column='blockchain_tx_id')

    batch_id = models.ForeignKey('Product_batch', on_delete=models.CASCADE, db_column='batch_id', null=True, blank=True)
    area_id = models.ForeignKey('Activity_area', on_delete=models.CASCADE, db_column='area_id')
    company_id = models.ForeignKey('Company', on_delete=models.CASCADE, db_column='company_id')
    certificate_id = models.ForeignKey('Certificate', on_delete=models.CASCADE, db_column='certificate_id')

    class Meta:
        db_table = 'chain_event'
        # manage = False
        verbose_name = 'Chain event'
        verbose_name_plural = 'Chain events'

    def __str__(self):
        return f"Event {self.event_id} | {self.area_id} | {self.location}"


class Batch_certificate(models.Model):
    cp_id = models.AutoField(primary_key=True, db_column='cp_id')

    batch_id = models.ForeignKey('Product_batch', on_delete=models.CASCADE, db_column='batch_id', null=True, blank=True)
    certificate_id = models.ForeignKey('Certificate', on_delete=models.CASCADE, db_column='certificate_id')

    class Meta:
        db_table = 'batch_certificate'
        
        # manage = False
        verbose_name ='Batch certificate'
        verbose_name_plural ='Batches certificate'

    def __str__(self):
        return f"Batch id {self.batch_id} | Certificate id {self.certificate_id}"


class Alert(models.Model):
    alert_id = models.AutoField(primary_key=True, db_column='alert_id')
    #
    ALERT_TYPE = [
        ('fraud_detected', "Oszustwo wykryte"),
        ('expiry_warning', "Ostrzeżenie o wygaśnięciu"),
        ('batch_issue', "Problem z partią"),
        ('compliance_breach', "Naruszenie zgodności ..."),
    ]

    alert_type = models.CharField(max_length=100, choices=ALERT_TYPE,db_column='alert_type')   
    description = models.CharField(max_length=1000, db_column='description')

    SEVERITY =[
        ('low', "Niskie"),
        ('medium', "Średnie"),
        ('high', "Wysokie"),
        ('critical', "Krytyczne"),
    ]
    severity = models.CharField(max_length=50, choices=SEVERITY,db_column='severity')
    STATUS = [
        ('done', 'Rozwiązane'),
        ('new', 'Nowe'),
        ('waiting', "Oczekujące"),
        ('realising', "W realizacji")
    ]
    status = models.CharField(max_length=50, choices=STATUS, default='new', db_column='status')

    event_id = models.ForeignKey('Chain_event', on_delete=models.CASCADE, db_column='event_id',null=True, blank=True)
    batch_id = models.ForeignKey('Product_batch', on_delete=models.CASCADE, db_column='batch_id', null=True, blank=True)

    class Meta:
        db_table = 'alert'
        # manage = False
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'

    def __str__(self):
        return f"{self.alert_id} - {self.alert_type}"


class Consumer_verification(models.Model):
    verification_id = models.AutoField(primary_key=True, db_column='verification_id')
    qr_code_scanned = models.CharField(max_length=500, db_column='qr_code_scanned')

    VERIFICATION_RESULT = [
        ('authentic', 'Autentyczny'),
        ('suspicious', 'Podejrzany'),
        ('fake', 'Podrobiony'),
    ]
    verification_result = models.CharField(max_length=50, db_column='verification_result', choices=VERIFICATION_RESULT)
    consumer_email = models.CharField(max_length=100, db_column='consumer_email')
    consumer_ip = models.CharField(max_length=45, db_column='consumer_ip')
    device_info = models.CharField(max_length=255, db_column='device_info')

    batch_id = models.ForeignKey('Product_batch', on_delete=models.CASCADE, db_column='batch_id', null=True, blank=True)

    class Meta:
        db_table = 'consumer_verification'
        # managed = False
        verbose_name = 'Consumer verification'
        verbose_name_plural = 'Consumers verification'

    def __str__(self):
        return self.qr_code_scanned


class Consumer_rating(models.Model):
    rating_id = models.AutoField(primary_key=True, db_column='rating_id')
    rating = models.IntegerField(null=True, db_column='rating', validators=[MinValueValidator(1), MaxValueValidator(5)]
        )
    comment = models.CharField(max_length=1000, db_column='comment')
    consumer_email = models.CharField(max_length=100, db_column='consumer_email')
    is_verified = models.IntegerField(default=0, db_column='is_verified')

    certificate_id = models.ForeignKey('Certificate', on_delete=models.CASCADE, db_column='certificate_id')

    class Meta:
        db_table = 'consumer_rating'
        # managed = False
        verbose_name = 'Consumer rating'
        verbose_name_plural = 'Consumer ratings'

    def __str__(self):
        return f"{self.consumer_email} - {self.rating}"


class Notification_cert(models.Model):
    notification_id = models.AutoField(primary_key=True, db_column='notification_id')
    
    NOTIFICATION_TYPE = [
        ('expiry_warning', 'Ostrzeżenie o wygaśnięciu'),
        ('status_change', 'Zmiana statusu'),

        ('suspension', 'Zawieszenie'),
        ('revocation', 'Anulowanie'),
    ]
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE, db_column='notification_type')
    expiry_date = models.DateField(null=True, blank=True, db_column='expiry_date')
    sent_to = models.CharField(max_length=100, db_column='sent_to')
    
    STATUS = [
        ('unsent', 'Niewysłane'),
        ('sent', 'Wysłane'),
        ('failed', 'Błąd'),
        ('bounced', 'Zwrócone'),]
    status = models.CharField(max_length=50, default='unsent', db_column='status', choices=STATUS)

    certificate_id = models.ForeignKey('Certificate', on_delete=models.CASCADE, db_column='certificate_id')

    class Meta:
        db_table = 'notification_cert'
        # managed = False
        verbose_name = 'Notification cert'
        verbose_name_plural = 'Notifications cert'

    def __str__(self):
        return f"Certificate id: {self.certificate_id} - {self.notification_type}"


class Fraud_report(models.Model):
    report_id = models.AutoField(primary_key=True, db_column='report_id')
    TYPE = [
        ('fake_id', "Fake ID"),
        ('fake_cert_id', "Fake certification ID"),
        ('other', 'Other')
    ]
    fraud_type = models.CharField(max_length=100, choices=TYPE, db_column='fraud_type')
    reporter_name = models.CharField(max_length=200, db_column='reporter_name', blank=False, null=False, default='')
    reporter_email = models.CharField(max_length=100, db_column='reporter_email')
    description = models.CharField(max_length=1000, db_column='description')
    STATUS = [
        ('new', 'Nowe'),
        ('investigating', 'W trakcie weryfikacji'),
        ('resolved', 'Rozwiązane'),
        ('rejected', 'Odrzucone')
    ]
    status = models.CharField(max_length=50, choices=STATUS, default='new', db_column='status')
    investigation_notes = models.CharField(max_length=1000, db_column='investigation_notes', blank=True, null=True, default='')

    batch_id = models.ForeignKey('Product_batch', on_delete=models.CASCADE, db_column='batch_id', null=True, blank=True)
    certificate_id = models.ForeignKey('Certificate', on_delete=models.CASCADE, db_column='certificate_id', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def check_and_reject_spam(self):
        three_minutes_ago = timezone.now() - timedelta(minutes=3)
        recent_reports = Fraud_report.objects.filter(
            reporter_email=self.reporter_email,
            status='new',
            created_at__gte=three_minutes_ago
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
        verbose_name = 'Fraud report'
        verbose_name_plural = 'Fraud reports'

    def __str__(self):
        return f"Fraud {self.fraud_type} reported by {self.reporter_email}"

class Certificate_status_history(models.Model):
    history_id = models.AutoField(primary_key=True, db_column='history_id')
    
    
    STATUS = [
        ('valid', 'Ważny'),
        ('expired', 'Wygasł'),
        ('suspended', 'Zawieszony'),
        ('revoked', 'Anulowany'),
    ]
    old_status = models.CharField(max_length=50, choices=STATUS, null=True, blank=True, db_column='old_status')
    new_status = models.CharField(max_length=50, choices=STATUS, null=False, db_column='new_status')
    
    changed_by_user_id = models.ForeignKey('Certifying_unit', on_delete=models.PROTECT, db_column='changed_by_user_id')
    changed_date = models.DateTimeField(auto_now_add=True, db_column='changed_date')

    reason = models.CharField(max_length=1000, db_column='reason')

    certificate_id = models.ForeignKey('Certificate', on_delete=models.CASCADE, db_column='certificate_id')

    class Meta:
        db_table = 'certificate_status_history'
        # managed = False
        verbose_name = 'Certificate status history'
        verbose_name_plural = 'Certificates status history'

    def __str__(self):
        return f"Id: {self.history_id} | changed: {self.changed_date}"


class Company_certifying_unit(models.Model):
    ccu_id = models.AutoField(primary_key=True, db_column='ccu_id')

    company_id = models.ForeignKey('Company', on_delete=models.CASCADE, db_column='company_id')
    certifying_unit_id = models.ForeignKey('Certifying_unit', on_delete=models.CASCADE,
                                           db_column='certifying_unit_id')

    class Meta:
        db_table = 'company_certifying_unit'
        # managed = False
        unique_together = ('company_id', 'certifying_unit_id')
        verbose_name = 'Company certifying unit'
        verbose_name_plural = 'Company certifying units'

    def __str__(self):
        return f"Company id: {self.company_id} | Certifying unit id: {self.certifying_unit_id}"


# konto producentów
class Producer(models.Model):
    producent_id = models.AutoField(primary_key=True, db_column='producer_id')    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='producer_user')
    name = models.CharField(max_length=200, null=False, db_column='name')
    address = models.CharField(max_length=500, db_column='address')
    producer_code = models.CharField(max_length=50, unique=True, null=False, db_column='producer_code')
    is_approved = models.BooleanField(default=False, db_column='is_approved')
    
    class Meta:
        db_table = 'producer'
        verbose_name = 'Producer'
        verbose_name_plural = 'Producers'

    def __str__(self):
        return self.name





# do generowania kodu walidacji jednostki certyfikujacej

class RegistrationCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registration_code'

    def __str__(self):
        return self.code