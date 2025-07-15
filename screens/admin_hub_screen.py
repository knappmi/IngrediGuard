from screens.base_screen import BaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.logger import Logger
import os
# from opentelemetry import trace
from utils.error_handler import error_handler
from utils.feature_flags import OCR_ENABLED

class AdminHubScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Admin Hub Screen for managing menu and settings."""
        # self.tracer = trace.get_tracer(__name__)
        Logger.info("Initializing Admin Hub Screen")
        super().__init__(**kwargs)

        self.layout.add_widget(self.make_button("Upload Menu", "upload"))
        self.layout.add_widget(self.make_button("Export Menu", on_press=self.export_menu))
        self.layout.add_widget(self.make_button("Edit Menu", "admin_menu"))
        self.layout.add_widget(self.make_button("User Management", "user_management"))
        if OCR_ENABLED:
            self.layout.add_widget(self.make_button("OCR Settings", "admin_settings"))

        self.add_logout_button("login")

    @error_handler
    def make_button(self, text, screen=None, on_press=None):
        # with self.tracer.start_as_current_span("admin_hub_screen.make_button") as span:
        #     span.set_attribute("text", text)
        #     span.set_attribute("screen", screen)
        #     span.set_attribute("on_press", on_press)

        Logger.info(f"AdminHubScreen: Creating button '{text}'")
        btn = Button(text=text, size_hint_y=None, height=50)
        if on_press:
            btn.bind(on_press=on_press)
        elif screen:
            btn.bind(on_press=lambda x: setattr(self.manager, 'current', screen))
        return btn

    @error_handler
    def export_menu(self, instance):
        """
        Export the current menu data to a CSV file in the 'Downloads' directory.
        """
        Logger.info("export_menu: Starting export process to Downloads.")
        try:
            from jnius import autoclass, cast
            import time
            import csv
            from io import StringIO

            # Android API classes
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            ContentValues = autoclass('android.content.ContentValues')
            MediaStore = autoclass('android.provider.MediaStore')
            Downloads = autoclass('android.provider.MediaStore$Downloads')
            Environment = autoclass('android.os.Environment')

            # Get the ContentResolver
            activity = PythonActivity.mActivity
            contentResolver = activity.getContentResolver()

            # Prepare CSV data in memory
            menu_data = self.manager.menu_data
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['item', 'ingredients'])
            for item in menu_data:
                ingredients_str = ', '.join(item['ingredients']) if isinstance(item['ingredients'], list) else item['ingredients']
                writer.writerow([item['item'], ingredients_str])
            csv_data = output.getvalue()
            output.close()

            # Set up file metadata
            file_name = f'menu_export_{int(time.time())}.csv'
            content_values = ContentValues()
            content_values.put("_display_name", file_name)
            content_values.put("mime_type", 'text/csv')
            content_values.put("relative_path", Environment.DIRECTORY_DOWNLOADS)
            
            # Insert the file into the MediaStore
            uri = contentResolver.insert(Downloads.EXTERNAL_CONTENT_URI, content_values)

            # Write the data to the file
            output_stream = contentResolver.openOutputStream(uri)
            output_stream.write(csv_data.encode())
            output_stream.close()

            # Create a message for the popup
            msg = f"Export successful!\n\nSaved as:\n{file_name}\n\nLocation: Your device's 'Downloads' folder."
            content = Label(text=msg, text_size=(self.width * 0.7, None), size_hint_y=None, halign='center')
            content.bind(texture_size=content.setter('size'))

            export_popup = Popup(
                title='Export Complete',
                content=content,
                size_hint=(0.8, 0.5),
                auto_dismiss=True
            )
            export_popup.open()
            Logger.info(f"Successfully exported menu to Downloads directory as {file_name}")

        except Exception as e:
            error_msg = f"Error during export: {e}"
            Logger.error(error_msg)
            self.set_status(error_msg)

    @error_handler
    def on_pre_enter(self):
        """Refresh menu data when entering the screen."""
        # with self.tracer.start_as_current_span("admin_hub_screen.on_pre_enter") as span:
        #     span.set_attribute("manager_db_exists", hasattr(self.manager, 'db'))

        Logger.info("AdminHubScreen: Refreshing menu data from database")
        try:
            self.manager.menu_data = self.manager.db.get_menu()
            Logger.info(f"AdminHubScreen: Loaded {len(self.manager.menu_data)} menu items from database")
        except Exception as e:
            Logger.error(f"AdminHubScreen: Error refreshing menu data: {str(e)}")
            self.set_status(f"Error loading menu: {str(e)}")
