from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .all_views import fraud_views
from .all_views.certificates_views import (
	add_cert, cert_succes, list_cert, cert_detail, 
	edit_cert, delete_cert, 
	certificate_history_view, certificate_history_export, certificate_change_log_api,
    
)
from ProjektSystemCertyfikacji.all_views import product_views
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
from django.contrib.humanize.templatetags.humanize import naturaltime 
   
from .all_views import dashboard_views
from .all_views.fraud_views import FraudReportViewSet
from .all_views import fraud_views

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
router.register(r'fraud-reports', FraudReportViewSet, basename='fraud-report')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('certificates/add/', add_cert, name='add_cert'),
    path('certificates/success/<int:cert_id>/', cert_succes, name='cert_succes'),
    path('certificates/list/', list_cert, name='list_cert'),

    path('certificates/<int:cert_id>/edit/', edit_cert, name='edit_cert'),
    path('certificates/<int:cert_id>/delete/', delete_cert, name='delete_cert'),

    path('certificates/<int:cert_id>/', cert_detail, name='cert_detail'),

    #path('certificates/<int:cert_id>/edit/', edit_cert, name='edit_cert'),
    #path('certificates/<int:cert_id>/delete/', delete_cert, name='delete_cert'),
    # API dla strony głównej
    # path('verify-qr-code/', verify_qr_code_api, name='verify_qr_code'),
    path('track-product/', track_product_api, name='track_product'),
    path('submit-rating/', submit_rating_api, name='submit_rating'),
    # path('submit-fraud-report/', submit_fraud_report_api, name='submit_fraud_report'),
    path('system-stats/', get_system_stats_api, name='system_stats'),
    path('certificate-details/', get_certificate_details_api, name='certificate_details'),

    # Historia zmian certyfikatu
    path('certificates/<int:cert_id>/history/', certificate_history_view, name='certificate_history'),
    path('certificates/<int:cert_id>/history/export/', certificate_history_export, name='certificate_history_export'),
    path('api/certificates/<int:cert_id>/changes/', certificate_change_log_api, name='certificate_change_log_api'),


    path('product-batches/', product_views.list_product_batches, name='list_product_batches'),
    path('product-batches/add/', product_views.add_product_batch, name='add_product_batch'),
    path('product-batches/<int:batch_id>/', product_views.product_batch_detail, name='product_batch_detail'),
    path('product-batches/<int:batch_id>/edit/', product_views.edit_product_batch, name='edit_product_batch'),
    path('product-batches/<int:batch_id>/delete/', product_views.delete_product_batch,name='delete_product_batch'),
path('product-batches/<int:batch_id>/recall/', product_views.recall_product_batch, name='recall_product_batch'),
    path('api/', include(router.urls)),

# Dashboard
        #path('dashboard/certificate/<int:certificate_id>/'),
    path('dashboard/', dashboard_views.control_dashboard, name='control_dashboard'),
    path('dashboard/certificate/<int:cert_id>/', dashboard_views.certificate_control_detail, name='certificate_control_detail'),
    path('dashboard/certificate/<int:cert_id>/revoke/', dashboard_views.revoke_certificate, name='revoke_certificate'),

    path('dashboard/fraud-reports/', dashboard_views.dashboard_fraud_reports, name='dashboard_fraud_reports'),
    path('dashboard/fraud-reports/<int:report_id>/', dashboard_views.dashboard_fraud_detail, name='dashboard_fraud_detail'),
]