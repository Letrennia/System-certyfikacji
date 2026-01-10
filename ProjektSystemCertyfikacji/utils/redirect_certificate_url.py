from ..models import Certificate
from django.shortcuts import get_object_or_404, redirect
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
import base64

def redirect_certificate(request, token):
    cert_id = decrypt_certificate_id(token)
    cert = get_object_or_404(Certificate, pk=cert_id)
    host = request.get_host()
    full_url = f'http://{host}/certificate/{token}/'
    return redirect(full_url)
    # return redirect('certificate_view', token=token)

# Deszyfrowanie tokenu do ID certyfikatu
def decrypt_certificate_id(token_str):
    try:
        f = Fernet(settings.FERNET_KEY)
        
        padding = '=' * (-len(token_str) % 4)
        token_bytes = base64.urlsafe_b64decode(token_str + padding)
        
        decrypted_bytes = f.decrypt(token_bytes)
        return int(decrypted_bytes.decode())
    except Exception:
        return None 