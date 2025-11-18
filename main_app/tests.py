# from django.test import TestCase

# # Create your tests here.

from django.test import TestCase
from .models import Certyfikat, Entity, Partia_produktow
from datetime import date

class ModelsVerboseTestCase(TestCase):

    def setUp(self):
        print("Tworzenie encji (Entity)...")
        self.entity = Entity.objects.create(
            entity_type="producer",
            name="Firma Test",
            email="test@firma.com",
            address="ul. Przykładowa 1",
            country="PL",
            registration_number="REG123456",
            blockchain_address="0xABC123",
            is_active=True,
            area_of_activity="prodction"
        )

        print("Tworzenie certyfikatu...")
        self.cert = Certyfikat.objects.create(
            certificate_id="CERT001",
            certificate_number="12345",
            certificate_type="inne",
            holder_entity_id=1,
            state="wazny",
            valid_from=date(2023,1,1),
            valid_to=date(2025,1,1),
            certificate_hash="HASH123",
            blockchain_address="0xHASH123"
        )

        print("Tworzenie partii produktów...")
        self.batch = Partia_produktow.objects.create(
            certificate_id=self.cert,
            name="Produkt Test",
            category="inne",
            codeCN="01010101",
            production_date=date(2023,1,1),
            producer_id=self.entity,
            expiration_date=date(2024,1,1),
            amount=100,
            unit="szt",
            blockchain_hash="HASHBATCH123"
        )

    def test_certyfikat_fields(self):
        print("Sprawdzanie pól certyfikatu...")
        with self.subTest(field="certificate_id"):
            self.assertEqual(self.cert.certificate_id, "CERT001")
        with self.subTest(field="state"):
            self.assertEqual(self.cert.state, "wazny")
        with self.subTest(field="valid_from < valid_to"):
            self.assertTrue(self.cert.valid_to > self.cert.valid_from)

    def test_entity_fields(self):
        print("Sprawdzanie pól encji...")
        with self.subTest(field="name"):
            self.assertEqual(self.entity.name, "Firma Test")
        with self.subTest(field="is_active"):
            self.assertTrue(self.entity.is_active)
        with self.subTest(field="area_of_activity"):
            self.assertEqual(self.entity.area_of_activity, "prodction")

    def test_batch_fields(self):
        print("Sprawdzanie pól partii produktów...")
        with self.subTest(field="certificate_id"):
            self.assertEqual(self.batch.certificate_id, self.cert)
        with self.subTest(field="producer_id"):
            self.assertEqual(self.batch.producer_id, self.entity)
        with self.subTest(field="amount"):
            self.assertEqual(self.batch.amount, 100)
