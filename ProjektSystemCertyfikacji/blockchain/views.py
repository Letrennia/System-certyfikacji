from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .core import get_blockchain
from ..models import Certyfikat, Partia_produktow
import json


@require_http_methods(["GET"])
def blockchain_status(request):
    blockchain = get_blockchain()

    return JsonResponse({
        "success": True,
        "chain_length": len(blockchain.chain),
        "is_valid": blockchain.is_chain_valid(),
        "latest_block": blockchain.get_latest_block().to_dict()
    })


@require_http_methods(["GET"])
def get_full_chain(request):
    blockchain = get_blockchain()

    return JsonResponse({
        "success": True,
        "chain": blockchain.get_chain(),
        "length": len(blockchain.chain)
    })


@require_http_methods(["GET"])
def verify_certificate_blockchain(request, certificate_id):
    blockchain = get_blockchain()
    exists = blockchain.verify_certificate(certificate_id)

    if exists:
        try:
            cert = Certyfikat.objects.get(certificate_id=certificate_id)
            return JsonResponse({
                "success": True,
                "verified": True,
                "certificate": {
                    "certificate_id": cert.certificate_id,
                    "certificate_number": cert.certificate_number,
                    "state": cert.state,
                    "valid_from": str(cert.valid_from),
                    "valid_to": str(cert.valid_to),
                    "blockchain_address": cert.blockchain_address
                }
            })
        except Certyfikat.DoesNotExist:
            return JsonResponse({
                "success": False,
                "verified": False,
                "error": "Certificate found in blockchain but not in database"
            })

    return JsonResponse({
        "success": True,
        "verified": False,
        "message": "Certificate not found in blockchain"
    })


@require_http_methods(["GET"])
def get_batch_history_blockchain(request, batch_id):
    blockchain = get_blockchain()
    history = blockchain.get_batch_history(batch_id)

    return JsonResponse({
        "success": True,
        "batch_id": batch_id,
        "history": history,
        "events_count": len(history)
    })


@require_http_methods(["GET"])
def get_certificate_batches_blockchain(request, certificate_id):
    blockchain = get_blockchain()
    batches = blockchain.get_certificate_batches(certificate_id)

    return JsonResponse({
        "success": True,
        "certificate_id": certificate_id,
        "batches": batches,
        "total_batches": len(batches)
    })


@csrf_exempt
@require_http_methods(["POST"])
def register_transfer(request):
    try:
        data = json.loads(request.body)
        batch_id = data.get('batch_id')
        from_entity = data.get('from_entity')
        to_entity = data.get('to_entity')

        if not all([batch_id, from_entity, to_entity]):
            return JsonResponse({
                "success": False,
                "error": "Missing required fields"
            }, status=400)

        try:
            batch = Partia_produktow.objects.get(batch_id=batch_id)
        except Partia_produktow.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Batch not found"
            }, status=404)

        blockchain = get_blockchain()
        transfer_hash = blockchain.register_transfer(batch_id, from_entity, to_entity)

        return JsonResponse({
            "success": True,
            "transfer_hash": transfer_hash,
            "message": "Transfer registered successfully"
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_http_methods(["GET"])
def validate_blockchain(request):
    blockchain = get_blockchain()
    is_valid = blockchain.is_chain_valid()

    return JsonResponse({
        "success": True,
        "is_valid": is_valid,
        "chain_length": len(blockchain.chain),
        "message": "Blockchain is valid" if is_valid else "Blockchain integrity compromised!"
    })