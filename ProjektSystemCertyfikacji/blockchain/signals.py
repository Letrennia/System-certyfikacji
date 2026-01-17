from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Certificate, Product_batch
from .core import get_blockchain, save_blockchain


@receiver(post_save, sender=Certificate)
def register_certificate_to_blockchain(sender, instance, created, **kwargs):
    if created:
        blockchain = get_blockchain()

        certificate_data = {
            "certificate_number": instance.certificate_number,
            "subject_type": instance.subject_type,  # ✅ ZMIENIONE z certificate_type
            "holder_company_id": instance.holder_company_id_id,
            "valid_from": instance.valid_from.isoformat(),
            "valid_to": instance.valid_to.isoformat(),
            "status": instance.status
        }

        blockchain_hash = blockchain.register_certificate(
            instance.certificate_id,
            certificate_data
        )

        instance.blockchain_address = blockchain_hash
        instance.save(update_fields=['blockchain_address'])


@receiver(post_save, sender=Product_batch)
def register_batch_to_blockchain(sender, instance, created, **kwargs):
    if created:
        blockchain = get_blockchain()

        batch_data = {
            "certificate_id": instance.certificate_id.certificate_id,
            "name": instance.name,
            "category": instance.category,
            "production_date": instance.production_date.isoformat(),
            "producer_id": instance.certifying_unit_id_id,
            "amount": float(instance.quantity),
            "unit": instance.unit_of_measure
        }

        blockchain_hash = blockchain.register_batch(
            instance.batch_id,
            batch_data
        )

        instance.blockchain_hash = blockchain_hash
        instance.save(update_fields=['blockchain_hash'])
        
        # Automatyczne utworzenie podłańcucha i rejestracja etapu produkcji
        subchain = blockchain.get_subchain(instance.batch_id)
        if subchain:
            # Pobranie lokalizacji z firmy producenta
            producer_location = ""
            try:
                producer_company = instance.certificate_id.holder_company_id
                producer_location = f"{producer_company.address}, {producer_company.country}"
            except:
                producer_location = "Unknown"
            
            # Rejestracja etapu produkcji w podłańcuchu
            subchain.register_production(
                harvest_date=instance.harvest_date.isoformat() if instance.harvest_date else None,
                production_date=instance.production_date.isoformat(),
                storage_conditions=instance.storage_conditions,
                location=producer_location,
                additional_data={
                    "batch_name": instance.name,
                    "category": instance.category,
                    "quantity": float(instance.quantity),
                    "unit": instance.unit_of_measure,
                    "transport_temperature": float(instance.transport_temperature) if instance.transport_temperature else None
                }
            )