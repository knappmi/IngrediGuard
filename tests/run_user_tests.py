#!/usr/bin/env python
"""
Test Runner for User Management Tests

This script runs all the unit and integration tests for the user management system.
"""

import unittest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all the test modules
from tests.test_user_database import TestUserDatabase
from tests.test_login_screen import TestLoginScreen
from tests.test_user_management_screen import TestUserManagementScreen

def run_all_tests():
    """Run all the user management tests."""
    # Create a test suite with all the test cases
    test_suite = unittest.TestSuite()
    
    # Add all the test classes
    test_suite.addTest(unittest.makeSuite(TestUserDatabase))
    test_suite.addTest(unittest.makeSuite(TestLoginScreen))
    test_suite.addTest(unittest.makeSuite(TestUserManagementScreen))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
