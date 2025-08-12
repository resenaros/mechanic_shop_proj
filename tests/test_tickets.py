from app import create_app
from app.models import db, Ticket, Customer, Mechanic, Inventory
import unittest
from datetime import date

class TestTicket(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for isolated testing every run
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            customer = Customer(name="Ticket Owner", email="owner@example.com", phone="555-0000", password="secret")
            mechanic = Mechanic(name="Ticket Mechanic", email="mech2@example.com", phone="1112223333", salary=40000, password="pw")
            db.session.add(customer)
            db.session.add(mechanic)
            db.session.commit()
            ticket = Ticket(customer_id=customer.id, ticket_date=date.today(), vin="VIN123")
            db.session.add(ticket)
            db.session.commit()
            self.ticket_id = ticket.id
            self.customer_id = customer.id
            self.mechanic_id = mechanic.id
            # Seed inventory for add-part test
            inv = Inventory(name="Brake Pads", price=49.99)
            db.session.add(inv)
            db.session.commit()
            self.inventory_id = inv.id

    def test_create_ticket(self):
        payload = {
            "customer_id": self.customer_id,
            "ticket_date": str(date.today()),
            "vin": "VIN999"
        }
        response = self.client.post('/tickets/', json=payload)  # Trailing slash matches your route
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['vin'], "VIN999")

    def test_create_ticket_missing_vin(self):
        payload = {
            "customer_id": self.customer_id,
            "ticket_date": str(date.today())
        }
        response = self.client.post('/tickets/', json=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_get_all_tickets(self):
        response = self.client.get('/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_my_tickets(self):
        # login first
        login_resp = self.client.post('/customers/login', json={
            "email": "owner@example.com",
            "password": "secret"
        })
        token = login_resp.json.get('auth_token')  # Use correct key based on your login response
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/tickets/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    # Optional: Add GET specific ticket route in your routes.py for this test to pass
    # @tickets_bp.route('/<int:ticket_id>', methods=['GET'])
    # def get_ticket(ticket_id):
    #     ticket = db.session.get(Ticket, ticket_id)
    #     if not ticket:
    #         return jsonify({"error": "Ticket not found."}), 404
    #     return ticket_schema.jsonify(ticket), 200

    def test_patch_ticket(self):
        payload = {"vin": "VIN111"}
        response = self.client.patch(f'/tickets/{self.ticket_id}', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['vin'], "VIN111")

    def test_assign_remove_mechanics(self):
        # Assign mechanic
        payload = {"add_mechanic_ids": [self.mechanic_id], "remove_mechanic_ids": []}
        response = self.client.put(f'/tickets/{self.ticket_id}', json=payload)
        self.assertEqual(response.status_code, 200)
        # Remove mechanic
        payload_remove = {"add_mechanic_ids": [], "remove_mechanic_ids": [self.mechanic_id]}
        response = self.client.put(f'/tickets/{self.ticket_id}', json=payload_remove)
        self.assertEqual(response.status_code, 200)

    def test_get_mechanics_for_ticket(self):
        response = self.client.get(f'/tickets/{self.ticket_id}/mechanics')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_assign_mechanic_to_ticket(self):
        response = self.client.put(f'/tickets/{self.ticket_id}/assign-mechanic/{self.mechanic_id}')
        self.assertEqual(response.status_code, 200)

    def test_remove_mechanic_from_ticket(self):
        # First, assign mechanic so removal won't fail
        self.client.put(f'/tickets/{self.ticket_id}/assign-mechanic/{self.mechanic_id}')
        response = self.client.put(f'/tickets/{self.ticket_id}/remove-mechanic/{self.mechanic_id}')
        self.assertEqual(response.status_code, 200)

    def test_add_part_to_ticket(self):
        payload = {"inventory_id": self.inventory_id, "quantity": 2}
        response = self.client.post(f'/tickets/{self.ticket_id}/add-part', json=payload)
        self.assertEqual(response.status_code, 200)

    # --- Negative tests ---
    def test_get_nonexistent_ticket(self):
        response = self.client.get('/tickets/999/mechanics')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json.get('error', '').lower())

    def test_patch_nonexistent_ticket(self):
        payload = {"vin": "DOESNOTEXIST"}
        response = self.client.patch('/tickets/999', json=payload)
        self.assertEqual(response.status_code, 404)

    def test_assign_nonexistent_mechanic(self):
        response = self.client.put(f'/tickets/{self.ticket_id}/assign-mechanic/999')
        self.assertEqual(response.status_code, 404)

    def test_remove_nonexistent_mechanic(self):
        response = self.client.put(f'/tickets/{self.ticket_id}/remove-mechanic/999')
        self.assertEqual(response.status_code, 404)

    def test_add_nonexistent_part(self):
        payload = {"inventory_id": 999, "quantity": 1}
        response = self.client.post(f'/tickets/{self.ticket_id}/add-part', json=payload)
        self.assertEqual(response.status_code, 404)
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose() 