import unittest
import os
import sqlite3
import time
from models.user_database import UserDatabase

class TestUserDatabase(unittest.TestCase):
    """Test cases for the UserDatabase class."""

    def setUp(self):
        """Set up the test environment with a temporary database."""
        self.test_db_path = "app_data/test_users.db"
        # Ensure we start fresh each time
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.user_db = UserDatabase(db_path=self.test_db_path)

    def tearDown(self):
        """Clean up after tests."""
        self.user_db.close()
        # Remove the test database file
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_default_admin_exists(self):
        """Test that a default admin user is created on initialization."""
        users = self.user_db.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['username'], 'admin')
        self.assertTrue(users[0]['is_admin'])
        self.assertTrue(users[0]['is_active'])

    def test_add_user(self):
        """Test adding a new user."""
        # Add a regular user
        success, message = self.user_db.add_user("testuser", "password123")
        self.assertTrue(success)
        self.assertIn("successfully", message)
        
        # Add an admin user
        success, message = self.user_db.add_user("adminuser", "adminpass", is_admin=True)
        self.assertTrue(success)
        
        # Check both users exist
        users = self.user_db.get_users()
        self.assertEqual(len(users), 3)  # Default admin + 2 new users
        
        # Verify their properties
        user_by_name = {user['username']: user for user in users}
        self.assertIn("testuser", user_by_name)
        self.assertIn("adminuser", user_by_name)
        self.assertFalse(user_by_name["testuser"]['is_admin'])
        self.assertTrue(user_by_name["adminuser"]['is_admin'])

    def test_add_duplicate_user(self):
        """Test adding a user with a username that already exists."""
        # First add is successful
        success, _ = self.user_db.add_user("testuser", "password123")
        self.assertTrue(success)
        
        # Second add with same username fails
        success, message = self.user_db.add_user("testuser", "different_password")
        self.assertFalse(success)
        self.assertIn("already exists", message)

    def test_authenticate_user(self):
        """Test user authentication."""
        # Add a test user
        self.user_db.add_user("testuser", "correct_password")
        
        # Correct authentication
        success, message, user_info = self.user_db.authenticate_user("testuser", "correct_password")
        self.assertTrue(success)
        self.assertIn("successful", message)
        self.assertEqual(user_info['username'], "testuser")
        
        # Wrong password
        success, message, user_info = self.user_db.authenticate_user("testuser", "wrong_password")
        self.assertFalse(success)
        self.assertIn("Invalid", message)
        self.assertIsNone(user_info)
        
        # Non-existent user
        success, message, user_info = self.user_db.authenticate_user("nonexistent", "password")
        self.assertFalse(success)
        self.assertIn("Invalid", message)
        self.assertIsNone(user_info)

    def test_disable_user(self):
        """Test disabling a user."""
        # Add a regular user
        self.user_db.add_user("testuser", "password123")
        
        # Disable the user
        success, message = self.user_db.toggle_user_status(2, False)  # ID 2 (after admin)
        self.assertTrue(success)
        
        # Check the user is disabled
        users = self.user_db.get_users()
        user = next((u for u in users if u['username'] == 'testuser'), None)
        self.assertIsNotNone(user)
        self.assertFalse(user['is_active'])
        
        # Authentication should fail for disabled users
        success, message, _ = self.user_db.authenticate_user("testuser", "password123")
        self.assertFalse(success)
        self.assertIn("disabled", message)

    def test_disable_last_admin(self):
        """Test that the last active admin cannot be disabled."""
        # Try to disable the default admin (which is the only admin)
        success, message = self.user_db.toggle_user_status(1, False)  # ID 1 is the default admin
        self.assertFalse(success)
        self.assertIn("last active admin", message)
        
        # Add another admin
        self.user_db.add_user("adminuser", "adminpass", is_admin=True)
        
        # Now we should be able to disable the original admin
        success, _ = self.user_db.toggle_user_status(1, False)
        self.assertTrue(success)
        
        # But we still can't disable the second admin
        success, message = self.user_db.toggle_user_status(2, False)  # ID 2 is the second admin
        self.assertFalse(success)
        self.assertIn("last active admin", message)

    def test_toggle_admin_privileges(self):
        """Test granting and revoking admin privileges."""
        # Add a regular user
        self.user_db.add_user("testuser", "password123")
        
        # Grant admin privileges
        success, message = self.user_db.toggle_user_admin(2, True)  # ID 2 (after admin)
        self.assertTrue(success)
        self.assertIn("granted", message)
        
        # Check the user is now an admin
        users = self.user_db.get_users()
        user = next((u for u in users if u['username'] == 'testuser'), None)
        self.assertIsNotNone(user)
        self.assertTrue(user['is_admin'])
        
        # Revoke admin privileges
        success, message = self.user_db.toggle_user_admin(2, False)
        self.assertTrue(success)
        self.assertIn("revoked", message)
        
        # Check the user is no longer an admin
        users = self.user_db.get_users()
        user = next((u for u in users if u['username'] == 'testuser'), None)
        self.assertIsNotNone(user)
        self.assertFalse(user['is_admin'])

    def test_change_password(self):
        """Test changing a user's password."""
        # Add a test user
        self.user_db.add_user("testuser", "old_password")
        
        # Change the password
        success, message = self.user_db.change_password(2, "new_password")  # ID 2 (after admin)
        self.assertTrue(success)
        
        # Old password should fail
        success, _, _ = self.user_db.authenticate_user("testuser", "old_password")
        self.assertFalse(success)
        
        # New password should work
        success, _, _ = self.user_db.authenticate_user("testuser", "new_password")
        self.assertTrue(success)

    def test_reset_database(self):
        """Test resetting the database."""
        # Add some users
        self.user_db.add_user("user1", "password1")
        self.user_db.add_user("user2", "password2")
        self.user_db.add_user("user3", "password3", is_admin=True)
        
        # Verify we have 4 users (3 + default admin)
        users = self.user_db.get_users()
        self.assertEqual(len(users), 4)
        
        # Reset the database
        success, _ = self.user_db.reset_database()
        self.assertTrue(success)
        
        # Verify we're back to just the default admin
        users = self.user_db.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['username'], 'admin')


if __name__ == '__main__':
    unittest.main()
