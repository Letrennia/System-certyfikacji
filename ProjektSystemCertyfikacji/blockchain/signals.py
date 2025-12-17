from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Certificate, Product_batch
from .core import get_blockchain


@receiver(post_save, sender=Certificate)
def register_certificate_to_blockchain(sender, instance, created, **kwargs):
    if created:
        blockchain = get_blockchain()

        certificate_data = {
            "certificate_number": instance.certificate_number,
            "certificate_type": instance.certificate_type,
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
