from rest_framework import serializers
from .models import (
    Certyfikat, Jednostka_certyfikujaca, Jednostka_certyfikat,
    Entity, Partia_produktow, Weryfikacja_konsumenta,
    Ocena_konsumenta, Alert, Fraud_report
)

class CertyfikatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certyfikat
        fields = '__all__'

class JednostkaCertyfikujacaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jednostka_certyfikujaca
        fields = '__all__'

class JednostkaCertyfikatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jednostka_certyfikat
        fields = '__all__'

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'

class PartiaProduktowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partia_produktow
        fields = '__all__'

class WeryfikacjaKonsumentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weryfikacja_konsumenta
        fields = '__all__'

class OcenaKonsumentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ocena_konsumenta
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class FraudReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fraud_report
        fields = '__all__'