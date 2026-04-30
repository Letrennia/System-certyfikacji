from ..models import Certificate
from django.shortcuts import get_object_or_404, redirect
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
import base64

# def redirect_certificate(request, token):
#     host = request.get_host()
#     full_url = f'http://{host}/certificate/{token}/'
#     return redirect(full_url)


def decrypt_certificate_id(token_str):
    try:
        f = Fernet(settings.FERNET_KEY)
        
        padding = '=' * (-len(token_str) % 4)
        token_bytes = base64.urlsafe_b64decode(token_str + padding)
        
        decrypted_bytes = f.decrypt(token_bytes)
        return int(decrypted_bytes.decode())
    except Exception:
        return None 
    

def encrypt_certificate_id(certificate_id):
    f = Fernet(settings.FERNET_KEY)
    token = f.encrypt(str(certificate_id).encode())
    return base64.urlsafe_b64encode(token).decode().rstrip('=')