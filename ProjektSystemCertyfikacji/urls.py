from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .all_views.views import (
    CertificateViewSet, CertifyingUnitViewSet,
    CertifyingUnitCertificatesViewSet, CompanyViewSet,
    ProductBatchViewSet, ConsumerVerificationViewSet,
    ConsumerRatingViewSet, AlertViewSet, FraudReportViewSet
)

router = DefaultRouter()
router.register(r'certificates', CertificateViewSet)
router.register(r'certifying-units', CertifyingUnitViewSet)
router.register(r'certifying-unit-certificates', CertifyingUnitCertificatesViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'product-batches', ProductBatchViewSet)
router.register(r'consumer-verifications', ConsumerVerificationViewSet)
router.register(r'consumer-ratings', ConsumerRatingViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'fraud-reports', FraudReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]