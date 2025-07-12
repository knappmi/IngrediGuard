from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.storage.jsonstore import JsonStore
from kivy import platform
from kivy.logger import Logger
import os
# from telemetry import setup_telemetry, KivyInstrumentor
# from opentelemetry import trace

# Import all screens
from screens.upload_screen import UploadScreen
from screens.admin_hub_screen import AdminHubScreen
from screens.allergy_screen import AllergyScreen
from screens.results_screen import ResultsScreen
from screens.admin_menu import AdminMenuScreen
from screens.landing_screen import LandingScreen
from screens.login_screen import LoginScreen
from utils.feature_flags import OCR_ENABLED
from models.menu_database import MenuDatabase

# Conditional import to avoid pulling in OCR dependencies when the feature is
# disabled.
if OCR_ENABLED:
    from screens.admin_settings_screen import AdminSettingsScreen

import csv

if platform == 'android':
    from android.permissions import request_permissions, Permission

class AllergyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Telemetry setup commented out
        # self.tracer = setup_telemetry()
        # KivyInstrumentor().instrument()

    def build(self):
        """Build the main application."""
        Logger.info("[AllergyApp] Building the application")

        Logger.info("[AllergyApp] Initializing ScreenManager")
        sm = ScreenManager()

        # Initialize database and attach it to ScreenManager
        Logger.info("[AllergyApp] Initializing MenuDatabase")
        sm.db = MenuDatabase()

        # Shared app data
        sm.filtered_df = None
        sm.is_admin = False

        # Load menu from disk if available
        Logger.info("[AllergyApp] Loading menu data from CSV if available")
        os.makedirs("app_data", exist_ok=True)
        menu_path = "app_data/menu.csv"
        if os.path.exists(menu_path):
            Logger.info(f"[AllergyApp] Menu file found at {menu_path}, loading data")
            with open(menu_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                menu_data = [row for row in reader]
                sm.menu_data = menu_data
                
                # Insert the menu data into the database
                Logger.info(f"[AllergyApp] Inserting {len(menu_data)} items into database")
                sm.db.clear_menu()  # Clear existing data
                sm.db.insert_menu(menu_data)
        else:
            Logger.info(f"[AllergyApp] No menu file found at {menu_path}, initializing empty data")
            sm.menu_data = []

        # Register all screens
        Logger.info("[AllergyApp] Registering screens")
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(LandingScreen(name='landing'))
        sm.add_widget(AllergyScreen(name='allergy'))
        sm.add_widget(ResultsScreen(name='results'))
        sm.add_widget(AdminHubScreen(name='admin_hub'))
        sm.add_widget(UploadScreen(name='upload'))
        sm.add_widget(AdminMenuScreen(name='admin_menu'))
        if OCR_ENABLED:
            sm.add_widget(AdminSettingsScreen(name='admin_settings'))

        return sm

    def on_start(self):
        """Request permissions on Android devices."""
        Logger.info("[AllergyApp] Requesting permissions on Android")
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA
            ])

    def on_stop(self):
        """Close the database connection when the app stops."""
        Logger.info("[AllergyApp] Closing database connection")
        # Close DB connection when app stops
        if hasattr(self.root, 'db'):
            self.root.db.close()

if __name__ == '__main__':
    AllergyApp().run()


