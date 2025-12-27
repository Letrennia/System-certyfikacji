from ..models import Certificate, decrypt_certificate_id
from django.shortcuts import get_object_or_404, redirect


def redirect_certificate(request, token):
    cert_id = decrypt_certificate_id(token)
    cert = get_object_or_404(Certificate, pk=cert_id)
    host = request.get_host()
    full_url = f'http://{host}/certificate/{token}/'
    return redirect(full_url)
    # return redirect('certificate_view', token=token)