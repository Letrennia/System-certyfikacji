from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .all_views.certificates_views import add_cert, cert_succes, list_cert, cert_detail

from .all_views.views import (
    CertificateViewSet, CertifyingUnitViewSet,
    CertifyingUnitCertificatesViewSet, CompanyViewSet,
    ProductBatchViewSet, ConsumerVerificationViewSet,
    ConsumerRatingViewSet, AlertViewSet, FraudReportViewSet,
) 
from .all_views.main_page_view import (
    # verify_qr_code_api, 
    track_product_api, submit_rating_api, get_system_stats_api, get_certificate_details_api
     # submit_fraud_report_api,
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
    path('admin/', admin.site.urls),
    path('certificates/add/', add_cert, name='add_cert'),
    path('certificates/success/<int:cert_id>/', cert_succes, name='cert_succes'),
    path('certificates/list/', list_cert, name='list_cert'),

    path('certificates/<int:cert_id>/', cert_detail, name='cert_detail'),

    # API dla strony głównej
    # path('verify-qr-code/', verify_qr_code_api, name='verify_qr_code'),
    path('track-product/', track_product_api, name='track_product'),
    path('submit-rating/', submit_rating_api, name='submit_rating'),
    # path('submit-fraud-report/', submit_fraud_report_api, name='submit_fraud_report'),
    path('system-stats/', get_system_stats_api, name='system_stats'),
    path('certificate-details/', get_certificate_details_api, name='certificate_details'),

    path('api/', include(router.urls)),
]