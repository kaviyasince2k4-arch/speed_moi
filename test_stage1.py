"""
Stage 1 Automated Verification Script for SPEED MOI.
Tests:
  1. Database tables and schema creation
  2. First-time admin creation
  3. Blocking duplicate/subsequent admin creation
  4. Authentication & password hashing verification
  5. Function creation and session persistence logic
  6. Previous functions listing and retrieval
  7. Password reset functionality
"""

import os
import unittest
from werkzeug.security import check_password_hash, generate_password_hash

# Ensure test uses a clean test db
os.environ['TESTING'] = '1'
os.environ['SPEED_MOI_DB'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'speed_moi_test.db')
import database
import app as flask_app

class Stage1TestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        flask_app.app.config['TESTING'] = True
        flask_app.app.config['WTF_CSRF_ENABLED'] = False
        self.client = flask_app.app.test_client()

        # Clean test tables
        conn = database.get_db()
        with conn:
            conn.execute("DELETE FROM contributions;")
            conn.execute("DELETE FROM functions;")
            conn.execute("DELETE FROM users;")
        conn.close()

    def tearDown(self):
        pass

    def test_01_first_time_admin_page(self):
        """When no user exists, login page should display first-time setup."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"First-Time Setup", response.data)
        self.assertIn(b"Create Admin Account", response.data)

    def test_02_create_admin_success_and_blocking(self):
        """Create admin account and verify that subsequent creation is blocked."""
        # 1. Create admin
        response = self.client.post('/create-admin', data={
            'username': 'admin',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin account created successfully", response.data)

        # 2. Database check
        user = database.get_user_by_username('admin')
        self.assertIsNotNone(user)
        self.assertTrue(check_password_hash(user['password_hash'], 'password123'))

        # 3. Attempt to create second admin - should be blocked!
        blocked_response = self.client.post('/create-admin', data={
            'username': 'intruder',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b"Admin account already exists", blocked_response.data)
        self.assertIsNone(database.get_user_by_username('intruder'))

    def test_03_login_and_logout(self):
        """Test authentication flow with valid and invalid credentials."""
        # Create user
        database.create_user('admin', generate_password_hash('correctpass'))

        # Invalid password
        bad_res = self.client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertIn(b"Invalid username or password", bad_res.data)

        # Valid password
        good_res = self.client.post('/login', data={
            'username': 'admin',
            'password': 'correctpass'
        }, follow_redirects=True)
        self.assertEqual(good_res.status_code, 200)
        self.assertIn(b"Setup Function", good_res.data)

        # Logout
        logout_res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b"You have been logged out successfully", logout_res.data)

    def test_04_function_setup_and_previous_functions(self):
        """Test creating a function and listing previous functions."""
        # Create admin and log in
        database.create_user('admin', generate_password_hash('password123'))
        self.client.post('/login', data={'username': 'admin', 'password': 'password123'})

        # Start a function
        create_res = self.client.post('/start-function', data={
            'function_name': 'Murugan & Valli Wedding',
            'coordinator_name': 'Sundaram Pillai',
            'function_date': '2026-10-15'
        }, follow_redirects=True)
        self.assertEqual(create_res.status_code, 200)
        self.assertIn(b"Murugan &amp; Valli Wedding", create_res.data)
        self.assertIn(b"Sundaram Pillai", create_res.data)

        # View previous functions
        list_res = self.client.get('/functions')
        self.assertEqual(list_res.status_code, 200)
        self.assertIn(b"Murugan &amp; Valli Wedding", list_res.data)
        self.assertIn(b"Currently Active", list_res.data)

    def test_05_password_reset(self):
        """Test reset password helper function."""
        database.create_user('admin', generate_password_hash('oldpassword'))
        new_hash = generate_password_hash('newsecretpass')
        updated = database.update_user_password('admin', new_hash)
        self.assertTrue(updated)

        user = database.get_user_by_username('admin')
        self.assertTrue(check_password_hash(user['password_hash'], 'newsecretpass'))

if __name__ == '__main__':
    unittest.main()
