import unittest
import os
from unittest.mock import MagicMock, patch
from kivy.uix.screenmanager import ScreenManager
from screens.login_screen import LoginScreen
from models.user_database import UserDatabase

class TestLoginScreen(unittest.TestCase):
    """Test cases for the LoginScreen class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test database
        self.test_db_path = "app_data/test_users.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        # Create and patch the UserDatabase to use our test database
        self.patcher = patch('screens.login_screen.UserDatabase')
        self.mock_user_db_class = self.patcher.start()
        self.mock_user_db = MagicMock()
        self.mock_user_db_class.return_value = self.mock_user_db
        
        # Create a mock screen manager
        self.manager = MagicMock(spec=ScreenManager)
        self.manager.is_admin = False
        self.manager.current_user = None
        self.manager.current = 'login'
        
        # Create the login screen
        self.login_screen = LoginScreen(name='login')
        self.login_screen.manager = self.manager

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_successful_login(self):
        """Test successful login with valid credentials."""
        # Set up mock return values for authentication
        self.mock_user_db.authenticate_user.return_value = (
            True, 
            "Authentication successful", 
            {"id": 1, "username": "testuser", "is_admin": False}
        )
        
        # Set the username and password
        self.login_screen.username_input.text = "testuser"
        self.login_screen.password_input.text = "password123"
        
        # Trigger the login function
        self.login_screen.login(None)
        
        # Check the user database was called correctly
        self.mock_user_db.authenticate_user.assert_called_with("testuser", "password123")
        
        # Check the screen manager was updated correctly
        self.assertEqual(self.manager.current, "landing")
        self.assertFalse(self.manager.is_admin)
        self.assertEqual(self.manager.current_user, {"id": 1, "username": "testuser", "is_admin": False})
        
        # Check the status label was updated
        self.assertIn("Welcome", self.login_screen.status_label.text)

    def test_admin_login(self):
        """Test successful login with admin credentials."""
        # Set up mock return values for admin authentication
        self.mock_user_db.authenticate_user.return_value = (
            True, 
            "Authentication successful", 
            {"id": 1, "username": "admin", "is_admin": True}
        )
        
        # Set the username and password
        self.login_screen.username_input.text = "admin"
        self.login_screen.password_input.text = "admin123"
        
        # Trigger the login function
        self.login_screen.login(None)
        
        # Check the screen manager was updated correctly
        self.assertEqual(self.manager.current, "landing")
        self.assertTrue(self.manager.is_admin)
        
        # Check the status label was updated
        self.assertIn("Welcome", self.login_screen.status_label.text)

    def test_failed_login(self):
        """Test login failure with invalid credentials."""
        # Set up mock return values for failed authentication
        self.mock_user_db.authenticate_user.return_value = (
            False, 
            "Invalid username or password", 
            None
        )
        
        # Set the username and password
        self.login_screen.username_input.text = "wronguser"
        self.login_screen.password_input.text = "wrongpass"
        
        # Trigger the login function
        self.login_screen.login(None)
        
        # Check the screen manager was not updated
        self.assertEqual(self.manager.current, "login")  # Should stay on login screen
        
        # Check the status label shows the error
        self.assertEqual(self.login_screen.status_label.text, "Invalid username or password")

    def test_empty_credentials(self):
        """Test login attempt with empty credentials."""
        # Set empty username and password
        self.login_screen.username_input.text = ""
        self.login_screen.password_input.text = ""
        
        # Trigger the login function
        self.login_screen.login(None)
        
        # Check the user database was not called
        self.mock_user_db.authenticate_user.assert_not_called()
        
        # Check the status label shows the error
        self.assertEqual(self.login_screen.status_label.text, "Please enter username and password")

    def test_disabled_account(self):
        """Test login attempt with disabled account."""
        # Set up mock return values for disabled account
        self.mock_user_db.authenticate_user.return_value = (
            False, 
            "Account is disabled", 
            None
        )
        
        # Set the username and password
        self.login_screen.username_input.text = "disabled_user"
        self.login_screen.password_input.text = "password123"
        
        # Trigger the login function
        self.login_screen.login(None)
        
        # Check the screen manager was not updated
        self.assertEqual(self.manager.current, "login")  # Should stay on login screen
        
        # Check the status label shows the error
        self.assertEqual(self.login_screen.status_label.text, "Account is disabled")

    @patch('screens.login_screen.Popup')
    def test_reset_app(self, mock_popup):
        """Test resetting the app."""
        # Mock the popup and its functionality
        mock_popup_instance = MagicMock()
        mock_popup.return_value = mock_popup_instance
        
        # Set up mock return value for reset_database
        self.mock_user_db.reset_database.return_value = (True, "Database reset successfully")
        
        # Create a mock popup to pass to reset_app
        mock_confirm_popup = MagicMock()
        
        # Call reset_app
        self.login_screen.reset_app(mock_confirm_popup)
        
        # Check the popup was dismissed
        mock_confirm_popup.dismiss.assert_called_once()
        
        # Check the user database was reset
        self.mock_user_db.reset_database.assert_called_once()
        
        # Check a new popup was created to show the success message
        mock_popup.assert_called()
        mock_popup_instance.open.assert_called_once()


if __name__ == '__main__':
    unittest.main()
