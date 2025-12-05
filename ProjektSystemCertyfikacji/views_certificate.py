from django.shortcuts import get_object_or_404, render
from django.http import Http404
from .models import Certyfikat
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
import base64
import logging

logger = logging.getLogger(__name__)

# def certificate_detail(request, certificate_id):
#     certificate = get_object_or_404(Certyfikat, certificate_id=certificate_id)
#     return render(request, 'certificate_detail.html', {'certificate': certificate})

def certificate_view(request, token):
    logger.debug(f"Próba odszyfrowania tokenu: {token}")
    
    try:
        padding_needed = len(token) % 4
        if padding_needed:
            token += '=' * (4 - padding_needed)
        
        logger.debug(f"Token po dodaniu paddingu: {token}")

        encrypted_data = base64.urlsafe_b64decode(token.encode())
        logger.debug(f"Dane po dekodowaniu base64: {encrypted_data[:20]}...")

        f = Fernet(settings.FERNET_KEY)
        decrypted_data = f.decrypt(encrypted_data)
        decrypted_id = decrypted_data.decode()
        
        logger.debug(f"Odszyfrowany ID: {decrypted_id}")
        certificate = get_object_or_404(Certyfikat, certificate_id=decrypted_id)
        
        return render(request, 'certificate_detail.html', {'certificate': certificate})
        
    except (InvalidToken, base64.binascii.Error) as e:
        logger.error(f"Błąd deszyfrowania tokenu: {str(e)}")
        return render(request, 'certificate/error.html', {
            'message': 'Nieprawidłowy lub uszkodzony link certyfikatu.'
        })
    except UnicodeDecodeError as e:
        logger.error(f"Błąd dekodowania danych: {str(e)}")
        return render(request, 'certificate/error.html', {
            'message': 'Nieprawidłowy format danych certyfikatu.'
        })
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {str(e)}")
        return render(request, 'certificate/error.html', {
            'message': 'Wystąpił nieoczekiwany błąd podczas ładowania certyfikatu.'
        })