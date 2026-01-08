
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .all_views.views import (
    CertificateViewSet, CertifyingUnitViewSet,
    CertifyingUnitCertificatesViewSet, CompanyViewSet,
    ProductBatchViewSet, ConsumerVerificationViewSet,
    ConsumerRatingViewSet, AlertViewSet, FraudReportViewSet,
) 
from .all_views.certificates_views import add_cert, cert_succes, list_cert


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
    path('admin/', admin.site.urls),
    path('certificates/add/', add_cert, name='add_cert'),
    path('certificates/success/<int:cert_id>/', cert_succes, name='cert_succes'),
    path('certificates/list/', list_cert, name='list_cert'),

    path('api/', include(router.urls)),
]