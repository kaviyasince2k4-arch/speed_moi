"""
Stage 2 Automated Verification Script for SPEED MOI.
Tests:
  1. Adding a contribution with manual entry (English and Tamil)
  2. Automatic Bill ID generation (SM-0001, SM-0002)
  3. Proper date and time persistence
  4. Individual bill receipt rendering and formatting (Indian currency format)
  5. Totals calculation in dashboard and contributions list
"""

import os
import unittest
from werkzeug.security import generate_password_hash

os.environ['TESTING'] = '1'
os.environ['SPEED_MOI_DB'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'speed_moi_test.db')
import database
import app as flask_app

class Stage2TestCase(unittest.TestCase):
    def setUp(self):
        flask_app.app.config['TESTING'] = True
        flask_app.app.config['WTF_CSRF_ENABLED'] = False
        self.client = flask_app.app.test_client()

        # Clean tables
        conn = database.get_db()
        with conn:
            conn.execute("DELETE FROM contributions;")
            conn.execute("DELETE FROM functions;")
            conn.execute("DELETE FROM users;")
        conn.close()

        # Create admin user
        database.create_user('admin', generate_password_hash('password123'))

        # Log in
        self.client.post('/login', data={'username': 'admin', 'password': 'password123'})

        # Create a test function
        self.func_id = database.create_function(
            function_name="Ramesh & Priya Wedding",
            coordinator_name="K. Murugan",
            function_date="2026-10-15"
        )
        with self.client.session_transaction() as sess:
            sess['function_id'] = self.func_id

    def test_01_save_contribution_first_bill(self):
        """Test recording first contribution: gets SM-0001, correct amount and bill receipt."""
        response = self.client.post('/save-contribution', data={
            'contributor_name': 'Ramesh Kumar',
            'native_place': 'Salem',
            'amount': '2000',
            'entry_date': '06-10-2026',
            'entry_time': '09:30 AM'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SM-0001", response.data)
        self.assertIn(b"Ramesh Kumar", response.data)
        self.assertIn(b"Salem", response.data)
        self.assertIn("₹2,000".encode('utf-8'), response.data)
        self.assertIn(b"Thank You. Your contribution is greatly valued.", response.data)

        # Check function counter updated
        fn = database.get_function(self.func_id)
        self.assertEqual(fn['next_bill_number'], 2)

    def test_02_save_contribution_second_bill_tamil_script(self):
        """Test recording second contribution with Tamil script."""
        # 1st entry
        self.client.post('/save-contribution', data={
            'contributor_name': 'First Person',
            'native_place': 'Madurai',
            'amount': '1000',
            'entry_date': '06-10-2026',
            'entry_time': '09:31 AM'
        })

        # 2nd entry in Tamil
        response = self.client.post('/save-contribution', data={
            'contributor_name': 'ரமேஷ் குமார்',
            'native_place': 'சேலம்',
            'amount': '50000',
            'entry_date': '06-10-2026',
            'entry_time': '09:35 AM'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SM-0002", response.data)
        # Check Tamil name and native place in response
        self.assertIn("ரமேஷ் குமார்".encode('utf-8'), response.data)
        self.assertIn("சேலம்".encode('utf-8'), response.data)
        self.assertIn(b"50,000", response.data)

    def test_03_contributions_list_and_totals(self):
        """Test All Contributions page lists entries and updates totals."""
        database.save_contribution(self.func_id, 'Person A', 'Chennai', 2000, '06-10-2026', '10:00 AM')
        database.save_contribution(self.func_id, 'Person B', 'Coimbatore', 3500, '06-10-2026', '10:05 AM')

        response = self.client.get('/contributions')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SM-0001", response.data)
        self.assertIn(b"SM-0002", response.data)
        self.assertIn(b"Person A", response.data)
        self.assertIn(b"Person B", response.data)
        self.assertIn(b"5,500", response.data)  # Total amount (2000 + 3500)

if __name__ == '__main__':
    unittest.main()
