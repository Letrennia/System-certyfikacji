from django.shortcuts import get_object_or_404, render
from .models import Certyfikat

#do testowania qr code

def certificate_detail(request, certificate_id):
    certificate = get_object_or_404(Certyfikat, certificate_id=certificate_id)
    return render(request, 'certificate_detail.html', {'certificate': certificate})
