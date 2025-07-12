import unittest
from io import StringIO
import sys
import os

# Add the root directory to the Python path to allow imports from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.menu_parser import parse_menu_stream

class TestMenuParser(unittest.TestCase):

    def test_standard_input(self):
        """TC-PARSE-01: Test with a well-formed, multi-line CSV."""
        csv_data = "item,ingredients\nSalad,\"Lettuce, Carrot, Cucumber\"\nBurger,\"Beef, Wheat, Cheese\""
        stream = StringIO(csv_data)
        result = parse_menu_stream(stream)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['item'], 'Salad')
        self.assertListEqual(result[0]['ingredients'], ['Lettuce', 'Carrot', 'Cucumber'])
        self.assertEqual(result[1]['item'], 'Burger')
        self.assertListEqual(result[1]['ingredients'], ['Beef', 'Wheat', 'Cheese'])

    def test_data_with_whitespace(self):
        """TC-PARSE-02: Test with extra spaces in the data."""
        csv_data = "item,ingredients\n  Pizza  ,\"  Dough, Tomato Sauce, Cheese  \""
        stream = StringIO(csv_data)
        result = parse_menu_stream(stream)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['item'], 'Pizza')
        self.assertListEqual(result[0]['ingredients'], ['Dough', 'Tomato Sauce', 'Cheese'])

    def test_empty_input(self):
        """TC-PARSE-03: Test with an empty string."""
        csv_data = ""
        stream = StringIO(csv_data)
        result = parse_menu_stream(stream)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_headers_only(self):
        """TC-PARSE-04: Test with a CSV containing only a header row."""
        csv_data = "item,ingredients"
        stream = StringIO(csv_data)
        result = parse_menu_stream(stream)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()