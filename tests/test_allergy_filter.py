import unittest
import sys
import os

# Add the root project directory to the Python path to allow imports from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.allergy_filter import perform_allergy_filter

class TestAllergyFilter(unittest.TestCase):

    def setUp(self):
        """Set up a standard menu for all tests."""
        self.menu_data = [
            {'item': 'Classic Burger', 'ingredients': 'Beef, Wheat Bun, Lettuce, Tomato'},
            {'item': 'Peanut Butter Shake', 'ingredients': 'Milk, Peanut Butter, Sugar'},
            {'item': 'Veggie Salad', 'ingredients': 'Lettuce, Cucumber, Bell Pepper'},
            {'item': 'Mac and Cheese', 'ingredients': 'Pasta, Cheese, Butter'}
        ]

    def test_simple_direct_match(self):
        """TC-FILTER-01: Test a direct, single allergen match."""
        result = perform_allergy_filter(self.menu_data, "Peanut")
        
        # Find the shake
        shake = next(item for item in result if item["item"] == "Peanut Butter Shake")
        self.assertFalse(shake['is_safe'])
        self.assertIn('peanut', shake['offending'])

    def test_no_match(self):
        """TC-FILTER-02: Test when the allergen is not present."""
        result = perform_allergy_filter(self.menu_data, "Soy")
        
        for item in result:
            self.assertTrue(item['is_safe'])
            self.assertEqual(len(item['offending']), 0)

    def test_expanded_map_match(self):
        """TC-FILTER-03: Test the ALLERGEN_MAP expansion (e.g., 'milk' -> 'cheese')."""
        result = perform_allergy_filter(self.menu_data, "Milk")
        
        # Find the Mac and Cheese
        mac_and_cheese = next(item for item in result if item["item"] == "Mac and Cheese")
        self.assertFalse(mac_and_cheese['is_safe'])
        self.assertIn('milk', mac_and_cheese['offending'])

    def test_multiple_allergens(self):
        """TC-FILTER-04: Test with a comma-separated list of allergens."""
        result = perform_allergy_filter(self.menu_data, "Wheat, Peanut")
        
        burger = next(item for item in result if item["item"] == "Classic Burger")
        shake = next(item for item in result if item["item"] == "Peanut Butter Shake")
        
        self.assertFalse(burger['is_safe'])
        self.assertIn('wheat', burger['offending'])
        
        self.assertFalse(shake['is_safe'])
        self.assertIn('peanut', shake['offending'])

    def test_case_insensitivity(self):
        """TC-FILTER-05: Test that allergen input and ingredient matching are case-insensitive."""
        result = perform_allergy_filter(self.menu_data, "WHEAT")
        burger = next(item for item in result if item["item"] == "Classic Burger")
        self.assertFalse(burger['is_safe'])
        self.assertIn('wheat', burger['offending'])

    def test_invalid_input(self):
        """TC-FILTER-06: Test with empty or whitespace-only input."""
        self.assertIsNone(perform_allergy_filter(self.menu_data, ""))
        self.assertIsNone(perform_allergy_filter(self.menu_data, "   "))
        self.assertIsNone(perform_allergy_filter(self.menu_data, " , "))
    
    def test_no_partial_word_match(self):
        """TC-FILTER-07: Ensure 'egg' doesn't match 'Veggie'."""
        menu = [{'item': 'Veggie Burger', 'ingredients': 'Veggie Patty, Bun'}]
        result = perform_allergy_filter(menu, "egg")
        self.assertTrue(result[0]['is_safe'])

    def test_substring_does_not_match(self):
        """TC-FILTER-08: Ensure a substring like 'gra' does not match 'grass'."""
        menu = [{'item': 'Lawn Clippings', 'ingredients': 'Fresh-cut grass'}]
        result = perform_allergy_filter(menu, "gra")
        self.assertTrue(result[0]['is_safe'])
        self.assertEqual(len(result[0]['offending']), 0)
    
    def test_cheese_as_allergen(self):
        # Simulated menu input
        menu_data = [
            {'item': 'Burger', 'ingredients': ['Beef', 'Wheat', 'Cheese']},
            {'item': 'Fruit Bowl', 'ingredients': ['Apple', 'Banana', 'Grapes']},
            {'item': 'Mac and Cheese', 'ingredients': ['Pasta', 'Milk', 'Cheddar Cheese']}
        ]

        # User inputs 'cheese' as an allergen
        allergen_input = 'cheese'

        # Perform filtering
        result = perform_allergy_filter(menu_data, allergen_input)

        # Assert results
        self.assertEqual(len(result), 3)

        burger = result[0]
        fruit_bowl = result[1]
        mac_and_cheese = result[2]

        # Burger and Mac and Cheese should be flagged as unsafe due to 'cheese'
        self.assertFalse(burger['is_safe'])
        self.assertIn('cheese', burger['offending'])

        self.assertTrue(fruit_bowl['is_safe'])
        self.assertEqual(fruit_bowl['offending'], [])

        self.assertFalse(mac_and_cheese['is_safe'])
        self.assertIn('cheese', mac_and_cheese['offending'])

if __name__ == '__main__':
    unittest.main() 