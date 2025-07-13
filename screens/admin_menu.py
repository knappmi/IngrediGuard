from screens.base_screen import BaseScreen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.logger import Logger
import os
import csv
# from opentelemetry import trace
from utils.error_handler import error_handler

class AdminMenuScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Admin Menu Screen for managing the menu items."""
        # self.tracer = trace.get_tracer(__name__)
        Logger.info("[AdminMenuScreen] Initializing Admin Menu Screen")
        super().__init__(**kwargs)

        # Title for Add Dish section
        title_label = Label(
            text="[b]Add Dish[/b]", 
            markup=True, 
            size_hint_y=None, 
            height=40,
            halign='center'
        )
        self.layout.add_widget(title_label)

        # Input fields for adding dishes
        input_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=90, spacing=10)
        
        self.item_input = TextInput(hint_text="Dish name", size_hint_y=None, height=40)
        self.ingredients_input = TextInput(hint_text="Ingredients (comma-separated)", size_hint_y=None, height=40)
        
        input_layout.add_widget(self.item_input)
        input_layout.add_widget(self.ingredients_input)
        self.layout.add_widget(input_layout)
        
        # Save and Clear buttons at the top
        top_btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10, padding=[0, 0, 0, 10])
        
        save_button = Button(
            text="Save",
            size_hint_x=0.7
        )
        save_button.bind(on_press=self.add_dish)
        top_btn_layout.add_widget(save_button)
        
        self.layout.add_widget(top_btn_layout)

        # Menu items scrollview
        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.menu_grid = GridLayout(cols=1, spacing=10, size_hint_y=None, size_hint_x=1)
        self.menu_grid.bind(minimum_height=self.menu_grid.setter('height'))
        self.scroll.add_widget(self.menu_grid)
        self.layout.add_widget(self.scroll)
        
        # Clear menu button placed under the menu list
        clear_button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=[10, 10, 10, 0])
        
        clear_button = Button(
            text="Clear Menu",
            background_color=(0.8, 0.2, 0.2, 1),
            size_hint_x=0.7,
            pos_hint={'center_x': 0.5}
        )
        clear_button.bind(on_press=self.confirm_clear_menu)
        clear_button_layout.add_widget(clear_button)
        self.layout.add_widget(clear_button_layout)
        
        # Back button at the bottom
        back_button = Button(text="Back", size_hint_y=None, height=40)
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_hub'))
        self.layout.add_widget(back_button)

    @error_handler
    def on_pre_enter(self):
        """Refresh the menu view when entering the screen."""
        Logger.info("[AdminMenuScreen] Refreshing menu view")
        self.debug_database()
        self.refresh_menu_view()

    @error_handler
    def debug_database(self):
        """Debug database connection and menu data."""
        try:
            Logger.info("[AdminMenuScreen] Debugging database connection")
            if not hasattr(self.manager, 'db'):
                Logger.error("[AdminMenuScreen] No database connection available (self.manager.db is None)")
                self.set_status("Error: Database connection not available")
                return
            
            # Try to get menu data
            menu_data = self.manager.db.get_menu()
            Logger.info(f"[AdminMenuScreen] Database connection successful, retrieved {len(menu_data)} items")
        except Exception as e:
            Logger.error(f"[AdminMenuScreen] Database debug error: {str(e)}")
            self.set_status(f"Database error: {str(e)}")

    @error_handler
    def refresh_menu_view(self):
        """Refresh the menu view by clearing and reloading the menu data."""
        Logger.info("[AdminMenuScreen] Refreshing menu data")
        self.menu_grid.clear_widgets()
        
        # with self.tracer.start_as_current_span("admin_menu.refresh_menu_view") as span:
        #     span.set_attribute("menu_items_count", len(self.manager.db.get_menu()))
        try:
            Logger.info("[AdminMenuScreen] Loading menu data from database")
            menu_data = self.manager.db.get_menu()

            header = GridLayout(cols=3, size_hint=(1, None), height=40, spacing=5)
            header.add_widget(Label(text='[b]Item[/b]', markup=True, size_hint_x=0.3, halign='left', valign='middle'))
            header.add_widget(Label(text='[b]Ingredients[/b]', markup=True, size_hint_x=0.6, halign='left', valign='middle'))
            header.add_widget(Label(text='[b]Delete[/b]', markup=True, size_hint_x=0.1, halign='center', valign='middle'))
            self.menu_grid.add_widget(header)

            for row in menu_data:
                item = row['item'].strip()
                ingredients = row['ingredients'].strip()
                dish_id = row['id']

                row_grid = GridLayout(cols=3, spacing=5, padding=5, size_hint=(1, None))
                row_grid.bind(minimum_height=row_grid.setter('height'))

                item_label = Label(text=item, size_hint_x=0.3, halign='left', valign='top')
                item_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)),
                                texture_size=lambda s, ts: s.setter('height')(s, ts[1]))

                ingredients_label = Label(text=ingredients, size_hint_x=0.6, halign='left', valign='top')
                ingredients_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)),
                                       texture_size=lambda s, ts: s.setter('height')(s, ts[1]))

                delete_btn = Button(text='X', size_hint_x=0.1, size_hint_y=None, height=40)

                def create_delete_callback(dish_id_for_callback):
                    return lambda instance: self.confirm_delete_dish(dish_id_for_callback)
                delete_btn.bind(on_press=create_delete_callback(dish_id))

                row_grid.add_widget(item_label)
                row_grid.add_widget(ingredients_label)
                row_grid.add_widget(delete_btn)
                self.menu_grid.add_widget(row_grid)

        except Exception as e:
            Logger.error(f"[AdminMenuScreen] Error refreshing menu view: {str(e)}")
            self.set_status(f"Error loading menu: {str(e)}")

    @error_handler
    def add_dish(self, instance):
        """Add a new dish to the menu."""
        # with self.tracer.start_as_current_span("admin_menu.add_dish") as span:
        #     span.set_attribute("item", self.item_input.text.strip())
        #     span.set_attribute("ingredients", self.ingredients_input.text.strip())

        Logger.info("[AdminMenuScreen] Adding new dish")
        item = self.item_input.text.strip()
        ingredients = self.ingredients_input.text.strip()

        if item and ingredients:
            try:
                self.manager.db.add_dish(item, ingredients)
                self.item_input.text = ""
                self.ingredients_input.text = ""
                self.refresh_menu_view()
                self.set_status("Dish added successfully.")
            except Exception as e:
                Logger.error(f"[AdminMenuScreen] Error adding dish: {str(e)}")
                self.set_status(f"Error adding dish: {str(e)}")
        else:
            self.set_status("Please enter both item and ingredients.")

    @error_handler
    def debug_db_connection(self):
        """Validate database connection state."""
        # with self.tracer.start_as_current_span("admin_menu.debug_db_connection") as span:
        #     span.set_attribute("manager_db_exists", hasattr(self.manager, 'db'))

        if not hasattr(self.manager, 'db'):
            Logger.error("[AdminMenuScreen] No db attribute in manager")
            return False
            
        try:
            db_obj = self.manager.db
            Logger.info(f"[AdminMenuScreen] Database object: {db_obj}, type: {type(db_obj)}")
            
            # Test calling a simple method
            menu_count = len(db_obj.get_menu())
            Logger.info(f"[AdminMenuScreen] Successfully got {menu_count} menu items from database")
            return True
        except Exception as e:
            import traceback
            Logger.error(f"[AdminMenuScreen] Database connection test failed: {str(e)}")
            Logger.error(f"[AdminMenuScreen] Exception: {traceback.format_exc()}")
            return False      

    @error_handler
    def delete_dish(self, dish_id):
        """Delete a dish from the menu."""
        # with self.tracer.start_as_current_span("admin_menu.delete_dish") as span:
        #     span.set_attribute("dish_id", dish_id)
            
        Logger.info(f"[AdminMenuScreen] Deleting dish with ID: {dish_id}")
        # First validate database connection
        if not self.debug_db_connection():
            self.set_status("Database connection error")
            return
                
        try:
            import traceback
            Logger.info(f"[AdminMenuScreen] Calling db.delete_dish({dish_id})")
            self.manager.db.delete_dish(dish_id)
            self.refresh_menu_view()
            self.set_status("Dish deleted successfully.")
        except Exception as e:
            Logger.error(f"[AdminMenuScreen] Error deleting dish: {str(e)}")
            Logger.error(f"[AdminMenuScreen] Exception traceback: {traceback.format_exc()}")
            self.set_status(f"Error deleting dish: {str(e)}")

    @error_handler
    def confirm_delete_dish(self, dish_id):
        """Show a confirmation dialog before deleting a dish."""
        Logger.info(f"[AdminMenuScreen] Confirming deletion for dish ID: {dish_id}")

        content = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        message_label = Label(
            text="Are you sure you want to delete this dish?",
            size_hint_y=None,
            height=80,
            text_size=(350, None),
            halign='center',
            valign='middle',
            markup=True
        )
        content.add_widget(message_label)

        button_layout = BoxLayout(
            spacing=20, 
            size_hint_y=None, 
            height=50,
            padding=(10, 0, 10, 10)
        )

        yes_button = Button(
            text="Yes",
            size_hint_x=0.5,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        no_button = Button(
            text="No",
            size_hint_x=0.5,
            background_color=(0.2, 0.6, 0.2, 1)
        )

        button_layout.add_widget(no_button)
        button_layout.add_widget(yes_button)
        content.add_widget(button_layout)

        popup = Popup(
            title="Confirm Deletion",
            content=content,
            size_hint=(0.8, None),
            height=250,
            auto_dismiss=True
        )

        def delete_and_dismiss(instance):
            self.delete_dish(dish_id)
            popup.dismiss()

        yes_button.bind(on_press=delete_and_dismiss)
        no_button.bind(on_press=popup.dismiss)
        
        popup.open()

    @error_handler
    def export_menu(self, instance):
        """Export the menu to a CSV file."""
        # with self.tracer.start_as_current_span("admin_menu.export_menu") as span:
        Logger.info("[AdminMenuScreen] Exporting menu to CSV")
        export_path = "app_data/exported_menu.csv"
        self.manager.db.export_to_csv(export_path)
        self.set_status(f"Menu exported to {export_path}.")

    @error_handler
    def confirm_clear_menu(self, instance):
        """Confirm clearing the entire menu."""
        # with self.tracer.start_as_current_span("admin_menu.confirm_clear_menu") as span:
        Logger.info("[AdminMenuScreen] Confirming clear menu")

        content = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        message_label = Label(
            text="Are you sure you want to clear the entire menu?",
            size_hint_y=None,
            height=80,
            text_size=(350, None),
            halign='center',
            valign='middle',
            markup=True
        )
        content.add_widget(message_label)

        button_layout = BoxLayout(
            spacing=20, 
            size_hint_y=None, 
            height=50,
            padding=(10, 0, 10, 10)
        )

        yes_button = Button(
            text="Yes",
            size_hint_x=0.5,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        no_button = Button(
            text="No",
            size_hint_x=0.5,
            background_color=(0.2, 0.6, 0.2, 1)
        )

        button_layout.add_widget(no_button)
        button_layout.add_widget(yes_button)
        content.add_widget(button_layout)

        popup = Popup(
            title="Confirm Clear Menu",
            content=content,
            size_hint=(0.8, None),
            height=300,
            auto_dismiss=True
        )

        def clear_and_dismiss(instance):
            self.clear_menu(popup)
            popup.dismiss()

        yes_button.bind(on_press=clear_and_dismiss)
        no_button.bind(on_press=popup.dismiss)
        
        popup.open()

    @error_handler
    def clear_menu(self, popup):
        """Clear the entire menu."""
        # with self.tracer.start_as_current_span("admin_menu.clear_menu") as span:
        Logger.info("[AdminMenuScreen] Clearing the entire menu")
        self.manager.db.clear_menu()
        popup.dismiss()
        self.refresh_menu_view()
        self.set_status("Menu has been cleared.")

    @error_handler
    def on_leave(self):
        """Called when leaving the screen."""
        # with self.tracer.start_as_current_span("admin_menu.on_leave") as span:
        Logger.info("[AdminMenuScreen] Leaving screen, clearing menu grid")
        self.menu_grid.clear_widgets()
        self.item_input.text = ""
        self.ingredients_input.text = ""
        super().on_leave()

