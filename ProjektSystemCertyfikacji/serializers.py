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

from rest_framework import serializers
from .models import Fraud_report, Certificate, Product_batch

class FraudReportSerializer(serializers.ModelSerializer):
    
    certificate_number = serializers.CharField(
        source='certificate_id.certificate_number', 
        read_only=True,
        allow_null=True
    )
    batch_name = serializers.CharField(
        source='batch_id.name', 
        read_only=True,
        allow_null=True
    )
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )
    fraud_type_display = serializers.CharField(
        source='get_fraud_type_display', 
        read_only=True
    )
    created_at_formatted = serializers.DateTimeField(
        source='created_at',
        format='%Y-%m-%d %H:%M',
        read_only=True
    )
    
    class Meta:
        model = Fraud_report
        fields = [
            'report_id',
            'fraud_type',
            'fraud_type_display',
	    'reporter_name', 
            'reporter_email',
            'description',
            'status',
            'status_display',
            'investigation_notes',
            'batch_id',
            'batch_name',
            'certificate_id',
            'certificate_number',
            'created_at',
            'created_at_formatted',
        ]
        read_only_fields = ['report_id', 'created_at']
        extra_kwargs = {
            'certificate_id': {'required': False, 'allow_null': True},
            'batch_id': {'required': False, 'allow_null': True},
            'investigation_notes': {'required': False, 'allow_null': True},
            'description': {'required': True},
            'reporter_email': {'required': True},
            'fraud_type': {'required': True},
        }