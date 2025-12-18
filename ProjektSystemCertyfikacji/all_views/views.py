from rest_framework import viewsets
from ..models import (
    Certificate, Certifying_unit, Certifying_unit_certificates,
    Company, Product_batch, Consumer_verification,
    Consumer_rating, Alert, Fraud_report
)
from ..serializers import (
    CertificateSerializer, CertifyingUnitSerializer,
    CertifyingUnitCertificatesSerializer, CompanySerializer,
    ProductBatchSerializer, ConsumerVerificationSerializer,
    ConsumerRatingSerializer, AlertSerializer, FraudReportSerializer
)

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

class CertifyingUnitViewSet(viewsets.ModelViewSet):
    queryset = Certifying_unit.objects.all()
    serializer_class = CertifyingUnitSerializer

class CertifyingUnitCertificatesViewSet(viewsets.ModelViewSet):
    queryset = Certifying_unit_certificates.objects.all()
    serializer_class = CertifyingUnitCertificatesSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class ProductBatchViewSet(viewsets.ModelViewSet):
    queryset = Product_batch.objects.all()
    serializer_class = ProductBatchSerializer

class ConsumerVerificationViewSet(viewsets.ModelViewSet):
    queryset = Consumer_verification.objects.all()
    serializer_class = ConsumerVerificationSerializer

class ConsumerRatingViewSet(viewsets.ModelViewSet):
    queryset = Consumer_rating.objects.all()
    serializer_class = ConsumerRatingSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

class FraudReportViewSet(viewsets.ModelViewSet):
    queryset = Fraud_report.objects.all()
    serializer_class = FraudReportSerializer