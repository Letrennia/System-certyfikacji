from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from ..models import Chain_event, Product_batch, Activity_area, Certificate, Company
from ..utils.geocoding import geocode_address
from datetime import datetime

def _get_user_company(user):
    if not user or not user.is_authenticated:
        return None
    try:
        return Company.objects.get(user=user, is_approved=True)
    except Company.DoesNotExist:
        return None


def _is_company_or_admin(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return _get_user_company(user) is not None


def _can_access_batch(user, batch):
    if user.is_superuser:
        return True
    company = _get_user_company(user)
    return company is not None and batch.certificate_id.holder_company_id == company


def _register_event_in_blockchain(event):
    try:
        from ..blockchain.core import get_blockchain

        blockchain = get_blockchain()
        batch_id   = event.batch_id.batch_id
        area_name  = event.area_id.name

        subchain = blockchain.get_subchain(batch_id)
        if subchain is None:
            batch = event.batch_id
            certificate_id = batch.certificate_id.certificate_id
            company_id     = event.company_id.company_id
            subchain = blockchain.create_subchain(batch_id, certificate_id, company_id)

        now_str   = event.event_timestamp.isoformat() if event.event_timestamp else None
        location  = event.location or ''
        company_id = event.company_id.company_id

        area_to_stage = {
            'production':   'producer',
            'preparation':  'processor',
            'introduction': 'distributor',
            'storage':      'distributor',
            'import':       'distributor',
            'export':       'retailer',
        }
        stage = area_to_stage.get(area_name, 'distributor')

        if stage == 'producer':
            block_hash = subchain.register_production(
                production_date=now_str,
                location=location,
            )
        elif stage == 'processor':
            block_hash = subchain.register_processing(
                processor_id=company_id,
                processing_date=now_str,
                storage_conditions='',
                transport_temperature=0.0,
                location=location,
                from_entity_id=company_id,
            )
        elif stage == 'retailer':
            block_hash = subchain.register_retail(
                retailer_id=company_id,
                retail_date=now_str,
                storage_conditions='',
                location=location,
                from_entity_id=company_id,
            )
        else:  # distributor (domyślny)
            block_hash = subchain.register_distribution(
                distributor_id=company_id,
                distribution_date=now_str,
                storage_conditions='',
                transport_temperature=0.0,
                location=location,
                from_entity_id=company_id,
            )

        from ..blockchain.core import save_blockchain
        save_blockchain()

        return block_hash

    except Exception as e:
        print(f"[Blockchain] Błąd rejestracji zdarzenia {event.event_id}: {e}")
        return None


# ── views ─────────────────────────────────────────────────────────────────────

@login_required
def list_chain_events(request, batch_id):
    if not _is_company_or_admin(request.user):
        return render(request, 'chain_events/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    batch = get_object_or_404(Product_batch, batch_id=batch_id)

    if not _can_access_batch(request.user, batch):
        return render(request, 'chain_events/error.html', {
            'msg': 'Brak uprawnień do tej partii produktów'
        })

    events = Chain_event.objects.filter(
        batch_id=batch
    ).select_related(
        'area_id', 'company_id', 'certificate_id'
    ).order_by('event_timestamp')

    locations_raw = list(
        events.exclude(location='')
              .values_list('location', flat=True)
              .distinct()
    )
    geo_data = []
    for loc in locations_raw:
        result = geocode_address(loc)
        if result:
            geo_data.append(result)

    return render(request, 'chain_events/list_chain_events.html', {
        'batch': batch,
        'events': events,
        'geo_data': geo_data,
    })


@login_required
def add_chain_event(request, batch_id):
    if not _is_company_or_admin(request.user):
        return render(request, 'chain_events/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    batch = get_object_or_404(Product_batch, batch_id=batch_id)

    if not _can_access_batch(request.user, batch):
        return render(request, 'chain_events/error.html', {
            'msg': 'Brak uprawnień do tej partii produktów'
        })

    activity_areas = Activity_area.objects.all()
    companies = Company.objects.filter(is_approved=True) if request.user.is_superuser else None

    if request.method == 'POST':
        try:
            area_id  = request.POST.get('area_id')
            location = request.POST.get('location', '').strip()

            if not area_id:
                messages.error(request, 'Pole "Obszar działalności" jest wymagane')
                return render(request, 'chain_events/add_chain_event.html', {
                    'batch': batch,
                    'activity_areas': activity_areas,
                    'companies': companies,
                })

            area = get_object_or_404(Activity_area, area_id=area_id)

            if request.user.is_superuser:
                company_id_val = request.POST.get('company_id')
                company = get_object_or_404(Company, company_id=company_id_val)
            else:
                company = _get_user_company(request.user)

            event = Chain_event(
                location=location,
                blockchain_hash='',
                blockchain_tx_id='',
                batch_id=batch,
                area_id=area,
                company_id=company,
                certificate_id=batch.certificate_id,
            )
            event.save()

            block_hash = _register_event_in_blockchain(event)
            if block_hash:
                event.blockchain_hash  = block_hash
                event.blockchain_tx_id = block_hash[:32]
                event.save(update_fields=['blockchain_hash', 'blockchain_tx_id'])

            messages.success(request, f'Zdarzenie "{area.get_name_display()}" zostało zarejestrowane'
                             + (' i zapisane w blockchain.' if block_hash else ' (blockchain niedostępny).'))
            return redirect('list_chain_events', batch_id=batch.batch_id)

        except Exception as e:
            messages.error(request, f'Błąd podczas rejestrowania zdarzenia: {str(e)}')

    return render(request, 'chain_events/add_chain_event.html', {
        'batch': batch,
        'activity_areas': activity_areas,
        'companies': companies,
    })


@login_required
def chain_event_detail(request, event_id):
    if not _is_company_or_admin(request.user):
        return render(request, 'chain_events/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    event = get_object_or_404(
        Chain_event.objects.select_related(
            'batch_id', 'area_id', 'company_id', 'certificate_id'
        ),
        event_id=event_id
    )

    if not _can_access_batch(request.user, event.batch_id):
        return render(request, 'chain_events/error.html', {
            'msg': 'Brak uprawnień do tego zdarzenia'
        })

    geo = geocode_address(event.location) if event.location else None

    return render(request, 'chain_events/chain_event_detail.html', {
        'event': event,
        'geo': geo,
    })


@login_required
def delete_chain_event(request, event_id):
    if not _is_company_or_admin(request.user):
        return render(request, 'chain_events/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    event = get_object_or_404(Chain_event, event_id=event_id)
    batch_id = event.batch_id.batch_id

    if not _can_access_batch(request.user, event.batch_id):
        return render(request, 'chain_events/error.html', {
            'msg': 'Brak uprawnień do usunięcia tego zdarzenia'
        })

    if request.method == 'POST':
        if event.blockchain_hash:
            try:
                from ..blockchain.core import get_blockchain, save_blockchain
                blockchain = get_blockchain()
                subchain = blockchain.get_subchain(event.batch_id.batch_id)
                if subchain:
                    subchain.add_block({
                        "type": "event_revocation",
                        "revoked_block_hash": event.blockchain_hash,
                        "batch_id": event.batch_id.batch_id,
                        "area": event.area_id.name,
                        "company_id": event.company_id.company_id,
                        "reason": "Deleted by user",
                        "timestamp": datetime.now().isoformat()
                    })
                    save_blockchain()
            except Exception as e:
                print(f"[Blockchain] Błąd rejestracji anulowania zdarzenia {event.event_id}: {e}")

        event.delete()
        messages.success(request, 'Zdarzenie zostało usunięte')
        return redirect('list_chain_events', batch_id=batch_id)

    return render(request, 'chain_events/delete_chain_event.html', {'event': event})


@login_required
def geocode_location_ajax(request):
    address = request.GET.get('address', '').strip()
    if not address:
        return JsonResponse({'error': 'Brak adresu'}, status=400)

    result = geocode_address(address)
    if result:
        return JsonResponse(result)

    return JsonResponse({'error': f'Nie znaleziono lokalizacji dla: {address}'}, status=404)