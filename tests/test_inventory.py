from app import create_app
from app.models import db, Inventory
import unittest

class TestInventory(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for isolated testing every run
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Create an inventory item to test GET, UPDATE, DELETE, etc.
            inv = Inventory(name="Oil Filter", price=19.99)
            db.session.add(inv)
            db.session.commit()
            self.part_id = inv.id  # Store the actual ID for robust tests

    def test_create_inventory(self):
        payload = {"name": "Brake Pads", "price": 49.99}
        # FIX: Use route with trailing slash, matches @inventory_bp.route('/', ...)
        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Brake Pads")

    def test_create_inventory_missing_price(self):
        # Negative test: missing required field
        payload = {"name": "No Price"}
        response = self.client.post('/inventory/', json=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_get_all_inventory(self):
        # FIX: Use route with trailing slash, matches route definition
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_specific_inventory(self):
        # Use self.part_id for robustness, not hardcoded 1
        response = self.client.get(f'/inventory/{self.part_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Oil Filter")

    def test_update_inventory(self):
        payload = {"name": "Updated Filter", "price": 24.99}
        response = self.client.put(f'/inventory/{self.part_id}', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Updated Filter")

    def test_patch_inventory(self):
        payload = {"price": 15.99}
        response = self.client.patch(f'/inventory/{self.part_id}', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['price'], 15.99)

    def test_delete_inventory(self):
        response = self.client.delete(f'/inventory/{self.part_id}')
        self.assertEqual(response.status_code, 200)

    def test_get_nonexistent_inventory(self):
        # Negative test: Should return 404 for missing part
        response = self.client.get('/inventory/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Part not found', response.json.get('error', ''))

    def test_update_nonexistent_inventory(self):
        payload = {"name": "Does Not Exist", "price": 1.99}
        response = self.client.put('/inventory/999', json=payload)
        self.assertEqual(response.status_code, 404)

    def test_patch_nonexistent_inventory(self):
        payload = {"price": 1.99}
        response = self.client.patch('/inventory/999', json=payload)
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_inventory(self):
        response = self.client.delete('/inventory/999')
        self.assertEqual(response.status_code, 404)
        
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose() 