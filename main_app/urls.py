from django.conf.urls.static import static
from django.contrib import admin
from ProjektSystemCertyfikacji import views_certificate
from django.urls import path, include
from django.views.generic import RedirectView

from main_app import settings

urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include('ProjektSystemCertyfikacji.urls')),
    path('certificate/<str:certificate_id>/', views_certificate.certificate_detail, name='certificate_detail'),
]

# 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)