from rest_framework import viewsets
from .models import (
    Certyfikat, Jednostka_certyfikujaca, Jednostka_certyfikat,
    Entity, Partia_produktow, Weryfikacja_konsumenta,
    Ocena_konsumenta, Alert, Fraud_report
)
from .serializers import (
    CertyfikatSerializer, JednostkaCertyfikujacaSerializer,
    JednostkaCertyfikatSerializer, EntitySerializer,
    PartiaProduktowSerializer, WeryfikacjaKonsumentaSerializer,
    OcenaKonsumentaSerializer, AlertSerializer, FraudReportSerializer
)

class CertyfikatViewSet(viewsets.ModelViewSet):
    queryset = Certyfikat.objects.all()
    serializer_class = CertyfikatSerializer

class JednostkaCertyfikujacaViewSet(viewsets.ModelViewSet):
    queryset = Jednostka_certyfikujaca.objects.all()
    serializer_class = JednostkaCertyfikujacaSerializer

class JednostkaCertyfikatViewSet(viewsets.ModelViewSet):
    queryset = Jednostka_certyfikat.objects.all()
    serializer_class = JednostkaCertyfikatSerializer

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

class PartiaProduktowViewSet(viewsets.ModelViewSet):
    queryset = Partia_produktow.objects.all()
    serializer_class = PartiaProduktowSerializer

class WeryfikacjaKonsumentaViewSet(viewsets.ModelViewSet):
    queryset = Weryfikacja_konsumenta.objects.all()
    serializer_class = WeryfikacjaKonsumentaSerializer

class OcenaKonsumentaViewSet(viewsets.ModelViewSet):
    queryset = Ocena_konsumenta.objects.all()
    serializer_class = OcenaKonsumentaSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

class FraudReportViewSet(viewsets.ModelViewSet):
    queryset = Fraud_report.objects.all()
    serializer_class = FraudReportSerializer