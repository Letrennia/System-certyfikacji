from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .core import get_blockchain, save_blockchain
from ..models import Certificate, Product_batch, Company
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
            cert = Certificate.objects.get(certificate_id=certificate_id)
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
        except Certificate.DoesNotExist:
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
            batch = Product_batch.objects.get(batch_id=batch_id)
        except Product_batch.DoesNotExist:
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


# ========== Supply Chain Track & Trace API ==========

@require_http_methods(["GET"])
def get_supply_chain_history(request, batch_id):
    """Pobranie pełnej historii łańcucha dostaw dla partii (od pola do stołu)"""
    blockchain = get_blockchain()
    history = blockchain.get_batch_supply_chain_history(batch_id)
    
    if history is None:
        return JsonResponse({
            "success": False,
            "error": "Subchain not found for this batch"
        }, status=404)
    
    return JsonResponse({
        "success": True,
        "batch_id": batch_id,
        "history": history,
        "events_count": len(history),
        "message": "Full supply chain history from field to table"
    })


@require_http_methods(["GET"])
def get_supply_chain_map(request, batch_id):
    try:
        try:
            batch = Product_batch.objects.get(batch_id=batch_id)
        except Product_batch.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Batch not found"
            }, status=404)

        geocode_param = request.GET.get('geocode', 'true').lower()
        geocode_enabled = geocode_param in ('true', '1', 'yes')
        
        blockchain = get_blockchain()
        map_data = blockchain.get_batch_supply_chain_map_data(batch_id, geocode=geocode_enabled)

        subchain = blockchain.get_subchain(batch_id)
        if subchain is None:
            return JsonResponse({"success": False, "error": "Subchain not found"}, status=404)
        map_data = subchain.get_supply_chain_map_data(geocode=geocode_enabled)

        if map_data is None:
            return JsonResponse({
                "success": False,
                "error": "Subchain not found for this batch"
            }, status=404)

        enriched_waypoints = []
        for waypoint in map_data.get("waypoints", []):
            enriched_waypoint = waypoint.copy()
            entity_id = waypoint.get("entity_id")
            if entity_id:
                try:
                    if waypoint.get("entity_type") == "producer":
                        from ..models import Certifying_unit
                        entity = Certifying_unit.objects.get(certifying_unit_id=entity_id)
                        enriched_waypoint["entity_info"] = {
                            "id": entity.certifying_unit_id,
                            "name": entity.name,
                            "address": entity.address,
                            "type": "certifying_unit"
                        }
                    else:
                        entity = Company.objects.get(company_id=entity_id)
                        enriched_waypoint["entity_info"] = {
                            "id": entity.company_id,
                            "name": entity.name,
                            "address": entity.address,
                            "country": entity.country,
                            "email": entity.email,
                            "phone": entity.phone,
                            "type": entity.company_type
                        }
                except Exception:
                    enriched_waypoint["entity_info"] = None
            
            enriched_waypoints.append(enriched_waypoint)
        map_data["waypoints"] = enriched_waypoints
        map_data["product_info"] = {
            "batch_id": batch.batch_id,
            "batch_name": batch.name,
            "category": batch.category,
            "quantity": float(batch.quantity),
            "unit": batch.unit_of_measure,
            "certificate_number": batch.certificate_id.certificate_number if batch.certificate_id else None,
            "production_date": batch.production_date.isoformat() if batch.production_date else None,
            "harvest_date": batch.harvest_date.isoformat() if batch.harvest_date else None
        }
        
        return JsonResponse({
            "success": True,
            "batch_id": batch_id,
            "map_data": map_data,
            "message": "Supply chain map data ready for visualization"
        })
    
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_subchain_address(request, batch_id):
    """Pobranie adresu podłańcucha dla partii"""
    blockchain = get_blockchain()
    address = blockchain.get_subchain_address(batch_id)
    
    if address is None:
        return JsonResponse({
            "success": False,
            "error": "Subchain address not found for this batch"
        }, status=404)
    
    return JsonResponse({
        "success": True,
        "batch_id": batch_id,
        "subchain_address": address
    })


@require_http_methods(["GET"])
def get_all_subchains(request):
    """Pobranie wszystkich podłańcuchów"""
    blockchain = get_blockchain()
    subchains = blockchain.get_all_subchains()
    
    return JsonResponse({
        "success": True,
        "subchains": subchains,
        "total_subchains": len(subchains)
    })


@csrf_exempt
@require_http_methods(["POST"])
def register_production(request):
    """Rejestracja etapu produkcji/zboru"""
    try:
        data = json.loads(request.body)
        batch_id = data.get('batch_id')
        harvest_date = data.get('harvest_date')
        production_date = data.get('production_date')
        storage_conditions = data.get('storage_conditions')
        location = data.get('location')
        
        if not all([batch_id, production_date, storage_conditions, location]):
            return JsonResponse({
                "success": False,
                "error": "Missing required fields: batch_id, production_date, storage_conditions, location"
            }, status=400)
        
        try:
            batch = Product_batch.objects.get(batch_id=batch_id)
        except Product_batch.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Batch not found"
            }, status=404)
        
        blockchain = get_blockchain()
        subchain = blockchain.get_subchain(batch_id)
        
        if subchain is None:
            # Utworzenie podłańcucha jeśli nie istnieje
            subchain = blockchain.create_subchain(
                batch_id,
                batch.certificate_id.certificate_id,
                batch.certifying_unit_id.certifying_unit_id
            )
        
        block_hash = subchain.register_production(
            harvest_date=harvest_date,
            production_date=production_date,
            storage_conditions=storage_conditions,
            location=location,
            additional_data=data.get('additional_data')
        )
        
        # Zapis blockchaina po modyfikacji podłańcucha
        save_blockchain()
        
        return JsonResponse({
            "success": True,
            "block_hash": block_hash,
            "message": "Production stage registered successfully"
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


@csrf_exempt
@require_http_methods(["POST"])
def register_processing(request):
    """Rejestracja etapu przetwarzania"""
    try:
        data = json.loads(request.body)
        batch_id = data.get('batch_id')
        processor_id = data.get('processor_id')
        processing_date = data.get('processing_date')
        storage_conditions = data.get('storage_conditions')
        transport_temperature = data.get('transport_temperature')
        location = data.get('location')
        from_entity_id = data.get('from_entity_id')
        
        if not all([batch_id, processor_id, processing_date, storage_conditions, 
                   transport_temperature is not None, location, from_entity_id]):
            return JsonResponse({
                "success": False,
                "error": "Missing required fields"
            }, status=400)
        
        try:
            batch = Product_batch.objects.get(batch_id=batch_id)
        except Product_batch.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Batch not found"
            }, status=404)
        
        blockchain = get_blockchain()
        subchain = blockchain.get_subchain(batch_id)
        
        if subchain is None:
            return JsonResponse({
                "success": False,
                "error": "Subchain not found for this batch. Register production first."
            }, status=404)
        
        block_hash = subchain.register_processing(
            processor_id=processor_id,
            processing_date=processing_date,
            storage_conditions=storage_conditions,
            transport_temperature=float(transport_temperature),
            location=location,
            from_entity_id=from_entity_id,
            additional_data=data.get('additional_data')
        )
        
        # Zapis blockchaina po modyfikacji podłańcucha
        save_blockchain()
        
        return JsonResponse({
            "success": True,
            "block_hash": block_hash,
            "message": "Processing stage registered successfully"
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


@csrf_exempt
@require_http_methods(["POST"])
def register_distribution(request):
    """Rejestracja etapu dystrybucji"""
    try:
        data = json.loads(request.body)
        batch_id = data.get('batch_id')
        distributor_id = data.get('distributor_id')
        distribution_date = data.get('distribution_date')
        storage_conditions = data.get('storage_conditions')
        transport_temperature = data.get('transport_temperature')
        location = data.get('location')
        from_entity_id = data.get('from_entity_id')
        
        if not all([batch_id, distributor_id, distribution_date, storage_conditions,
                   transport_temperature is not None, location, from_entity_id]):
            return JsonResponse({
                "success": False,
                "error": "Missing required fields"
            }, status=400)
        
        try:
            batch = Product_batch.objects.get(batch_id=batch_id)
        except Product_batch.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Batch not found"
            }, status=404)
        
        blockchain = get_blockchain()
        subchain = blockchain.get_subchain(batch_id)
        
        if subchain is None:
            return JsonResponse({
                "success": False,
                "error": "Subchain not found for this batch. Register production first."
            }, status=404)
        
        block_hash = subchain.register_distribution(
            distributor_id=distributor_id,
            distribution_date=distribution_date,
            storage_conditions=storage_conditions,
            transport_temperature=float(transport_temperature),
            location=location,
            from_entity_id=from_entity_id,
            additional_data=data.get('additional_data')
        )
        
        # Zapis blockchaina po modyfikacji podłańcucha
        save_blockchain()
        
        return JsonResponse({
            "success": True,
            "block_hash": block_hash,
            "message": "Distribution stage registered successfully"
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


@csrf_exempt
@require_http_methods(["POST"])
def register_retail(request):
    """Rejestracja etapu sprzedaży detalicznej"""
    try:
        data = json.loads(request.body)
        batch_id = data.get('batch_id')
        retailer_id = data.get('retailer_id')
        retail_date = data.get('retail_date')
        storage_conditions = data.get('storage_conditions')
        location = data.get('location')
        from_entity_id = data.get('from_entity_id')
        
        if not all([batch_id, retailer_id, retail_date, storage_conditions, location, from_entity_id]):
            return JsonResponse({
                "success": False,
                "error": "Missing required fields"
            }, status=400)
        
        try:
            batch = Product_batch.objects.get(batch_id=batch_id)
        except Product_batch.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Batch not found"
            }, status=404)
        
        blockchain = get_blockchain()
        subchain = blockchain.get_subchain(batch_id)
        
        if subchain is None:
            return JsonResponse({
                "success": False,
                "error": "Subchain not found for this batch. Register production first."
            }, status=404)
        
        block_hash = subchain.register_retail(
            retailer_id=retailer_id,
            retail_date=retail_date,
            storage_conditions=storage_conditions,
            location=location,
            from_entity_id=from_entity_id,
            additional_data=data.get('additional_data')
        )
        
        # Zapis blockchaina po modyfikacji podłańcucha
        save_blockchain()
        
        return JsonResponse({
            "success": True,
            "block_hash": block_hash,
            "message": "Retail stage registered successfully"
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