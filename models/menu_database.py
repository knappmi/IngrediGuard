import sqlite3
import os
import csv

class MenuDatabase:
    """
    A class to manage the menu database using SQLite.
    It provides methods to add, delete, and retrieve dishes,
    as well as export the menu to a CSV file.
    """

    def __init__(self, db_path="app_data/menu.db"):
        """
        Initializes the database connection and creates the menu table if it
        doesn't exist.
        """
        self.manager = None  # Add manager attribute to prevent crashes
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        """Creates the menu table if it doesn't already exist."""
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS menu (
                        id INTEGER PRIMARY KEY,
                        item TEXT NOT NULL,
                        ingredients TEXT NOT NULL
                    )
                """)
        except sqlite3.Error as e:
            print(f"Database error in create_table: {e}")

    def get_menu(self):
        """Retrieves the entire menu from the database."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id, item, ingredients FROM menu")
                rows = cursor.fetchall()
                # Convert list of tuples to list of dictionaries
                menu_list = [{'id': r[0], 'item': r[1], 'ingredients': r[2]} for r in rows]
                return menu_list
        except sqlite3.Error as e:
            print(f"Database error in get_menu: {e}")
            return []

    def add_dish(self, item, ingredients):
        """Adds a new dish to the menu."""
        try:
            with self.conn:
                self.conn.execute("INSERT INTO menu (item, ingredients) VALUES (?, ?)", (item, ingredients))
        except sqlite3.Error as e:
            print(f"Database error in add_dish: {e}")

    def delete_dish(self, dish_id):
        """Deletes a dish from the menu by its ID."""
        try:
            with self.conn:
                self.conn.execute("DELETE FROM menu WHERE id = ?", (dish_id,))
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def insert_menu(self, items):
        cursor = self.conn.cursor()
        formatted_items = []
        for item in items:
            ingredients = item['ingredients']
            # Convert list of ingredients to comma-separated string if it's a list
            if isinstance(ingredients, list):
                ingredients = ', '.join(ingredients)
            formatted_items.append((item['item'], ingredients))
        cursor.executemany('INSERT INTO menu (item, ingredients) VALUES (?, ?)', formatted_items)
        self.conn.commit()

    def export_to_csv(self, path="app_data/exported_menu.csv"):
        dishes = self.get_all_dishes()
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'item', 'ingredients'])
            writer.writerows(dishes)

    def clear_menu(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM menu')
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
