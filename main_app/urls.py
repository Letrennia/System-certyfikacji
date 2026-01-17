
from django.conf.urls.static import static
from django.contrib import admin
from ProjektSystemCertyfikacji.all_views import views_certificate
from django.urls import path, include
from django.views.generic import RedirectView
from ProjektSystemCertyfikacji.all_views.certificates_views import add_cert, cert_succes, list_cert,  cert_detail
from ProjektSystemCertyfikacji.all_views import c_sign_in_view, c_sign_out_view, c_sign_up_view, main_page_view, p_sign_up_view, choose_account_view, producer_main_view
from ProjektSystemCertyfikacji.utils import redirect_certificate_url
from main_app import settings
from ProjektSystemCertyfikacji.all_views import product_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_page_view.main_page, name='home'),  
    path('blockchain/', include('ProjektSystemCertyfikacji.blockchain.urls')),
    path('api/', include('ProjektSystemCertyfikacji.urls')),
    path('redirect/<str:token>/', redirect_certificate_url.redirect_certificate, name='redirect_certificate'),
    path('certificate/<path:token>/ratings/', views_certificate.fetch_ratings, name='fetch_ratings'), 
    path('certificate/<path:token>/', views_certificate.certificate_view, name='certificate_view'), 
    path('report_fraud/<path:token>/', views_certificate.report_fraud, name='report_fraud'),

    path('login/', c_sign_in_view.sign_in, name='login'),
    path('logout/', c_sign_out_view.sign_out, name='logout'),
    path('register/', c_sign_up_view.sign_up, name='register'), #jednostka cert
    path('register_producer/', p_sign_up_view.sign_up, name='register_producer'), #producent
    path('account_type/', choose_account_view.account_type, name='account_type'),
    path('producer_main/', producer_main_view.p_main_page, name='producer_main'),
    # path('main_page/', main_page_view.main_page, name='main'),


    path('certificates/add/', add_cert, name='add_cert'),
    path('certificates/success/<int:cert_id>/', cert_succes, name='cert_succes'),
    path('certificates/list/', list_cert, name='list_cert'),
    path('certificates/<int:cert_id>/', cert_detail, name='cert_detail'),

    path('product-batches/', product_views.list_product_batches, name='list_product_batches'),
    path('product-batches/add/', product_views.add_product_batch, name='add_product_batch'),
    path('product-batches/<int:batch_id>/', product_views.product_batch_detail, name='product_batch_detail'),
    path('product-batches/<int:batch_id>/edit/', product_views.edit_product_batch, name='edit_product_batch'),
    path('product-batches/<int:batch_id>/delete/', product_views.delete_product_batch,name='delete_product_batch'),
    path('product-batches/<int:batch_id>/recall/', product_views.recall_product_batch, name='recall_product_batch'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

