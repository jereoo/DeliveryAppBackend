"""Tests for vehicle manufacturer/model catalog."""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from delivery.models import VehicleManufacturer, VehicleModelSpec
from delivery.vehicle_catalog_validation import max_capacity_for_spec


class VehicleCatalogTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_migration_seeded_catalog(self):
        self.assertGreaterEqual(VehicleManufacturer.objects.count(), 10)
        self.assertGreaterEqual(VehicleModelSpec.objects.count(), 25)
        ford = VehicleManufacturer.objects.get(name='Ford')
        self.assertTrue(ford.model_specs.filter(name='F-150').exists())

    def test_catalog_api_lists_manufacturers_and_models(self):
        response = self.client.get('/api/vehicle-catalog/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ford = next(item for item in response.data if item['name'] == 'Ford')
        f150 = next(model for model in ford['models'] if model['name'] == 'F-150')
        self.assertEqual(f150['max_payload_lb'], 3325)
        self.assertIn('max_capacity_kg', f150)

    def test_max_capacity_respects_fleet_cap(self):
        spec = VehicleModelSpec.objects.get(manufacturer__name='Ford', name='F-350 Super Duty')
        self.assertEqual(max_capacity_for_spec(spec, 'kg'), 2000)
        self.assertEqual(max_capacity_for_spec(spec, 'lb'), 4400)
