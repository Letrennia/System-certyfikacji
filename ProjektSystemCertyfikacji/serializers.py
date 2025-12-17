from rest_framework import serializers
from .models import (
    Certificate, Certifying_unit, Certifying_unit_certificates,
    Company, Product_batch, Consumer_verification,
    Consumer_rating, Alert, Fraud_report
)

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'

class CertifyingUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifying_unit
        fields = '__all__'

class CertifyingUnitCertificatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifying_unit_certificates
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class ProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_batch
        fields = '__all__'

class ConsumerVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer_verification
        fields = '__all__'

class ConsumerRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer_rating
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class FraudReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fraud_report
        fields = '__all__'