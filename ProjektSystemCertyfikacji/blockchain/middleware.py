# middleware.py
import time
from django.http import JsonResponse


class BlockchainTimingMiddleware:
    """Proste mierzenie czasu trwania requestów powiązanych z blockchainem."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "blockchain" in request.path:
            start = time.time()
            response = self.get_response(request)
            duration = round(time.time() - start, 4)
            response["X-Blockchain-Timing"] = str(duration)
            return response

        return self.get_response(request)
