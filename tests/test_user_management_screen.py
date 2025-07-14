import unittest
import os
from unittest.mock import MagicMock, patch
from kivy.uix.screenmanager import ScreenManager
from screens.user_management_screen import UserManagementScreen
from models.user_database import UserDatabase

class TestUserManagementScreen(unittest.TestCase):
    """Integration tests for the UserManagementScreen."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test database path
        self.test_db_path = "app_data/test_users.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        # Create an actual UserDatabase for integration testing
        self.user_db = UserDatabase(db_path=self.test_db_path)
        
        # Patch the UserDatabase class to return our test instance
        self.patcher = patch('screens.user_management_screen.UserDatabase')
        self.mock_user_db_class = self.patcher.start()
        self.mock_user_db_class.return_value = self.user_db
        
        # Create a mock screen manager
        self.manager = MagicMock(spec=ScreenManager)
        
        # Create the user management screen
        self.user_management_screen = UserManagementScreen(name='user_management')
        self.user_management_screen.manager = self.manager

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        self.user_db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    @patch('screens.user_management_screen.Popup')
    def test_add_user(self, mock_popup):
        """Test adding a new user through the UI."""
        # Set up mock popup
        mock_popup_instance = MagicMock()
        mock_popup.return_value = mock_popup_instance
        
        # Set the form fields
        self.user_management_screen.username_input.text = "newuser"
        self.user_management_screen.password_input.text = "newpassword"
        self.user_management_screen.admin_button.is_admin = False
        
        # Trigger add user
        self.user_management_screen.add_user(None)
        
        # Verify popup was shown
        mock_popup.assert_called_once()
        mock_popup_instance.open.assert_called_once()
        
        # Check database for the new user
        users = self.user_db.get_users()
        self.assertEqual(len(users), 2)  # Default admin + new user
        
        new_user = next((u for u in users if u['username'] == 'newuser'), None)
        self.assertIsNotNone(new_user)
        self.assertFalse(new_user['is_admin'])
        self.assertTrue(new_user['is_active'])
        
        # Check authentication works
        success, _, _ = self.user_db.authenticate_user("newuser", "newpassword")
        self.assertTrue(success)

    @patch('screens.user_management_screen.Popup')
    def test_toggle_admin_status(self, mock_popup):
        """Test toggling admin status through the UI."""
        # Set up mock popup
        mock_popup_instance = MagicMock()
        mock_popup.return_value = mock_popup_instance
        
        # Add a test user
        self.user_db.add_user("testuser", "password123")
        
        # Refresh the UI to show the new user
        self.user_management_screen.refresh_user_list()
        
        # Create a mock button with properties the toggle_user_admin function expects
        mock_button = MagicMock()
        mock_button.user_id = 2  # ID for the new user
        mock_button.is_admin = True  # Make them an admin
        
        # Call the toggle function
        self.user_management_screen.toggle_user_admin(mock_button)
        
        # Verify popup was shown
        mock_popup.assert_called_once()
        mock_popup_instance.open.assert_called_once()
        
        # Check the user is now an admin
        users = self.user_db.get_users()
        test_user = next((u for u in users if u['username'] == 'testuser'), None)
        self.assertIsNotNone(test_user)
        self.assertTrue(test_user['is_admin'])

    @patch('screens.user_management_screen.Popup')
    def test_toggle_user_status(self, mock_popup):
        """Test enabling/disabling users through the UI."""
        # Set up mock popup
        mock_popup_instance = MagicMock()
        mock_popup.return_value = mock_popup_instance
        
        # Add a test user
        self.user_db.add_user("testuser", "password123")
        
        # Refresh the UI
        self.user_management_screen.refresh_user_list()
        
        # Create a mock button with properties the toggle_user_status function expects
        mock_button = MagicMock()
        mock_button.user_id = 2  # ID for the new user
        mock_button.make_active = False  # Disable them
        
        # Call the toggle function
        self.user_management_screen.toggle_user_status(mock_button)
        
        # Verify popup was shown
        mock_popup.assert_called_once()
        mock_popup_instance.open.assert_called_once()
        
        # Check the user is now disabled
        users = self.user_db.get_users()
        test_user = next((u for u in users if u['username'] == 'testuser'), None)
        self.assertIsNotNone(test_user)
        self.assertFalse(test_user['is_active'])
        
        # Authentication should fail
        success, message, _ = self.user_db.authenticate_user("testuser", "password123")
        self.assertFalse(success)
        self.assertIn("disabled", message)

    @patch('screens.user_management_screen.Popup')
    def test_reset_database(self, mock_popup):
        """Test resetting the database through the UI."""
        # Set up mock popup for both confirmation and result
        mock_popup_instance = MagicMock()
        mock_popup.return_value = mock_popup_instance
        
        # Add some test users
        self.user_db.add_user("user1", "password1")
        self.user_db.add_user("user2", "password2")
        
        # Verify we have 3 users (default admin + 2 new)
        users = self.user_db.get_users()
        self.assertEqual(len(users), 3)
        
        # Create a mock confirmation popup
        mock_confirm_popup = MagicMock()
        
        # Call reset_database
        self.user_management_screen.reset_database(mock_confirm_popup)
        
        # Verify the confirmation popup was dismissed
        mock_confirm_popup.dismiss.assert_called_once()
        
        # Verify the result popup was shown
        mock_popup.assert_called_once()
        mock_popup_instance.open.assert_called_once()
        
        # Check we're back to just the default admin
        users = self.user_db.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['username'], 'admin')


if __name__ == '__main__':
    unittest.main()
