from app import create_app
from app.models import db, Mechanic
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for isolated testing
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            mechanic = Mechanic(name="Test Mechanic", email="mech@example.com", phone="1234567890", salary=50000, password="mechanicpass")
            db.session.add(mechanic)
            db.session.commit()
            self.mechanic_id = mechanic.id  # Always use actual ID

 # --- ADD THIS HELPER METHOD! ---
    def get_auth_token(self):
        """
        Helper to log in as the test mechanic and get an auth token.
        This allows other tests to authenticate without returning from test methods.
        """
        payload = {
            "email": "mech@example.com",
            "password": "mechanicpass"
        }
        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.json)
        return response.json['auth_token']
    
    def test_create_mechanic(self):
        payload = {
            "name": "Gabriel",
            "email": "GabrielA@example.com",
            "phone": "0987654321",
            "salary": 75000,
            "password": "mechanicpass"
        }
        # FIX: Use trailing slash to match @mechanics_bp.route('/', ...)
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Gabriel")

    def test_create_mechanic_missing_email(self):
        payload = {
            "name": "NoEmail",
            "phone": "0987654321",
            "salary": 75000,
            "password": "mechanicpass"
        }
        response = self.client.post('/mechanics/', json=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_login_mechanic(self):
        payload = {
            "email": "mech@example.com",
            "password": "mechanicpass"
        }
        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.json)

    def test_login_mechanic_wrong(self):
        payload = {
            "email": "mech@example.com",
            "password": "wrongpass"
        }
        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 401)

    def test_get_all_mechanics(self):
        # FIX: Use trailing slash to match route
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_mechanics_paginated(self):
        response = self.client.get('/mechanics/?page=1&per_page=1')
        self.assertEqual(response.status_code, 200)

    def test_get_specific_mechanic(self):
        response = self.client.get(f'/mechanics/{self.mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test Mechanic')

    def test_update_mechanic(self):
        token = self.get_auth_token()
        payload = {
            "name": "Updated Name",
            "email": "mech@example.com",
            "phone": "1112223333",
            "salary": 60000,
            "password": "newpass"
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.put(f'/mechanics/{self.mechanic_id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Name')

    def test_patch_mechanic(self):
        token = self.get_auth_token()
        payload = {
            "salary": 90000
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.patch(f'/mechanics/{self.mechanic_id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['salary'], 90000)

    def test_delete_mechanic(self):
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete(f'/mechanics/{self.mechanic_id}', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_popular_mechanics(self):
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)

    def test_search_mechanic(self):
        response = self.client.get('/mechanics/search?name=Test')
        self.assertEqual(response.status_code, 200)

    # --- Negative tests for non-existent mechanic ---
    def test_get_nonexistent_mechanic(self):
        response = self.client.get('/mechanics/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json.get('error', '').lower())

    def test_update_nonexistent_mechanic(self):
        token = self.get_auth_token()
        payload = {
            "name": "Does Not Exist",
            "email": "no@email.com",
            "phone": "0000000000",
            "salary": 0,
            "password": "none"
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.put('/mechanics/999', json=payload, headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_patch_nonexistent_mechanic(self):
        token = self.get_auth_token()
        payload = {"salary": 0}
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.patch('/mechanics/999', json=payload, headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_mechanic(self):
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete('/mechanics/999', headers=headers)
        self.assertEqual(response.status_code, 404)
        
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose() 