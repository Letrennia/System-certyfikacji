
from django.conf.urls.static import static
from django.contrib import admin
from ProjektSystemCertyfikacji.all_views import views_certificate
from django.urls import path, include
from django.views.generic import RedirectView
from ProjektSystemCertyfikacji.all_views import c_sign_in_view, c_sign_out_view, c_sign_up_view, main_page_view, add_certificate_view

from main_app import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ProjektSystemCertyfikacji.blockchain.urls')),
    path('api/', include('ProjektSystemCertyfikacji.urls')),
    path('certificate/<path:token>/', views_certificate.certificate_view, name='certificate_view'), 
    path('report_fraud/<path:token>/', views_certificate.report_fraud, name='report_fraud'),
    # path('certificate/<str:certificate_id>/', views_certificate.certificate_detail, name='certificate_detail'),
    path('login/', c_sign_in_view.sign_in, name='login'),
    path('logout/', c_sign_out_view.sign_out, name='logout'),
    path('register/', c_sign_up_view.sign_up, name='register'),
    path('main_page/', main_page_view.main_page, name='main'),
    path('add_certificate/', add_certificate_view.add_certificate, name='add_certificate')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

