from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CertyfikatViewSet, JednostkaCertyfikujacaViewSet,
    JednostkaCertyfikatViewSet, EntityViewSet,
    PartiaProduktowViewSet, WeryfikacjaKonsumentaViewSet,
    OcenaKonsumentaViewSet, AlertViewSet, FraudReportViewSet
)

router = DefaultRouter()
router.register(r'certyfikaty', CertyfikatViewSet)
router.register(r'jednostki-certyfikujace', JednostkaCertyfikujacaViewSet)
router.register(r'jednostki-certyfikaty', JednostkaCertyfikatViewSet)
router.register(r'entities', EntityViewSet)
router.register(r'partie-produktow', PartiaProduktowViewSet)
router.register(r'weryfikacje', WeryfikacjaKonsumentaViewSet)
router.register(r'oceny', OcenaKonsumentaViewSet)
router.register(r'alerty', AlertViewSet)
router.register(r'fraud-reports', FraudReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
