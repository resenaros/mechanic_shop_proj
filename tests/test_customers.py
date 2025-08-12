from app import create_app
from app.models import db, Customer
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for isolated tests every run
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Create a simple customer for login and get-by-id
            customer = Customer(name="Test User", email="john@example.com", phone="555-1234", password="secret")
            db.session.add(customer)
            db.session.commit()
            self.customer_id = customer.id  # Always use this, not hardcoded 1

    # Helper to get a fresh token for the test user
    def get_auth_token(self):
        payload = {
            "email": "john@example.com",
            "password": "secret"
        }
        response = self.client.post('/customers/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.json)
        return response.json['auth_token']

    def test_create_customer(self):
        payload = {
            "name": "Shredder Doe",
            "email": "Shredder@example.com",
            "phone": "555-1234",
            "password": "secret"
        }
        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Shredder Doe")

    def test_create_customer_missing_email(self):
        # Negative test: missing required field
        payload = {
            "name": "Missing Email",
            "phone": "555-1234",
            "password": "secret"
        }
        response = self.client.post('/customers/', json=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_login_customer(self):
        payload = {
            "email": "john@example.com",
            "password": "secret"
        }
        response = self.client.post('/customers/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.json)
        self.auth_token = response.json.get('auth_token')

    def test_login_customer_wrong(self):
        payload = {
            "email": "john@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post('/customers/login', json=payload)
        # Your route correctly returns 401 for invalid login, so expect 401 here
        self.assertEqual(response.status_code, 401)

    def test_get_all_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_customers_paginated(self):
        response = self.client.get('/customers/?page=1&per_page=1')
        self.assertEqual(response.status_code, 200)

    def test_get_specific_customer(self):
        # Use self.customer_id for robustness
        response = self.client.get(f'/customers/{self.customer_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test User')

    def test_update_customer(self):
        token = self.get_auth_token()
        payload = {
            "name": "John Updated",
            "email": "john@example.com",
            "phone": "555-9999",
            "password": "newpass"
        }
        headers = {'Authorization': f'Bearer {token}'}
        # FIX: Use correct route with ID in path!
        response = self.client.put(f'/customers/{self.customer_id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John Updated')

    def test_patch_customer(self):
        token = self.get_auth_token()
        payload = {
            "name": "Patched Name"
        }
        headers = {'Authorization': f'Bearer {token}'}
        # FIX: Use correct route with ID in path!
        response = self.client.patch(f'/customers/{self.customer_id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Patched Name')

    def test_delete_customer(self):
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        # FIX: Use correct route with ID in path!
        response = self.client.delete(f'/customers/{self.customer_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        # Optionally, check the response message
        self.assertIn('successfully deleted', response.json.get('message', ''))
        
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose() 