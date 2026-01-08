
from django.conf.urls.static import static
from django.contrib import admin
from ProjektSystemCertyfikacji.all_views import views_certificate
from django.urls import path, include
from django.views.generic import RedirectView
from ProjektSystemCertyfikacji.all_views.certificates_views import add_cert, cert_succes, list_cert,  cert_detail
from ProjektSystemCertyfikacji.all_views import c_sign_in_view, c_sign_out_view, c_sign_up_view, main_page_view
from ProjektSystemCertyfikacji.utils import redirect_certificate_url
from main_app import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ProjektSystemCertyfikacji.blockchain.urls')),
    path('api/', include('ProjektSystemCertyfikacji.urls')),
    path('redirect/<str:token>/', redirect_certificate_url.redirect_certificate, name='redirect_certificate'),
    path('certificate/<path:token>/', views_certificate.certificate_view, name='certificate_view'), 
    path('report_fraud/<path:token>/', views_certificate.report_fraud, name='report_fraud'),

    path('login/', c_sign_in_view.sign_in, name='login'),
    path('logout/', c_sign_out_view.sign_out, name='logout'),
    path('register/', c_sign_up_view.sign_up, name='register'),
    path('main_page/', main_page_view.main_page, name='main'),


    path('certificates/add/', add_cert, name='add_cert'),
    path('certificates/success/<int:cert_id>/', cert_succes, name='cert_succes'),
    path('certificates/list/', list_cert, name='list_cert'),
    path('certificates/<int:cert_id>/', cert_detail, name='cert_detail'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

