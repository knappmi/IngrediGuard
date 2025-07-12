from screens.base_screen import BaseScreen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.storage.jsonstore import JsonStore
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import os
# from opentelemetry import trace
from utils.error_handler import error_handler

class AdminSettingsScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Admin Screen for managing settings"""
        # self.tracer = trace.get_tracer(__name__)
        Logger.info("[AdminSettingsScreen] Initializing Admin Settings Screen")
        super().__init__(**kwargs)

        os.makedirs("app_data", exist_ok=True)
        self.store = JsonStore(os.path.join("app_data", "config.json"))

        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        title_layout.add_widget(Label(text="Set OCR API Key"))
        
        info_button = Button(
            text="i",
            size_hint=(None, None),
            size=(80, 80),
            font_size='20sp'
        )
        info_button.bind(on_press=self.show_api_info)
        title_layout.add_widget(info_button)
        
        self.layout.add_widget(title_layout)
        
        self.api_input = TextInput(hint_text="Enter your OCR API Key", multiline=False)
        self.layout.add_widget(self.api_input)

        save_button = Button(text="Save API Key")
        save_button.bind(on_press=self.save_key)
        self.layout.add_widget(save_button)

        self.status_label = Label(text="")
        self.layout.add_widget(self.status_label)

        self.add_back_button("upload")

    @error_handler
    def on_pre_enter(self):
        """Load the API key from the store when entering the screen."""
        # with self.tracer.start_as_current_span("admin_settings_screen.on_pre_enter") as span:
        #     span.set_attribute("store_exists", self.store.exists("ocr_key"))

        Logger.info("[AdminSettingsScreen] Loading API key from store")
        if self.store.exists("ocr_key"):
            Logger.info("[AdminSettingsScreen] API key found in store")
            self.api_input.text = self.store.get("ocr_key")["value"]
        else:
            Logger.info("[AdminSettingsScreen] No API key found in store")
            self.api_input.text = ""
            self.status_label.text = "No API Key found. Please enter one."

    @error_handler
    def save_key(self, instance):
        """Save the API key to the store."""
        # with self.tracer.start_as_current_span("admin_settings_screen.save_key") as span:
        #     span.set_attribute("instance", instance)

        Logger.info("[AdminSettingsScreen] Saving API key")
        key = self.api_input.text.strip()
        if key:
            Logger.info("[AdminSettingsScreen] Saving API key to store")
            self.store.put("ocr_key", value=key)
            self.status_label.text = "API Key saved."
        else:
            Logger.warning("[AdminSettingsScreen] API key is empty")
            self.status_label.text = "API Key cannot be empty."

    @error_handler
    def show_api_info(self, instance):
        """Show a popup with information about getting an OCR API key."""
        # with self.tracer.start_as_current_span("admin_settings_screen.show_api_info") as span:
        #     span.set_attribute("instance", instance)

        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        info_text = (
            "[b]How to get an OCR API Key:[/b]\n\n"
            "1. Go to [ref=https://ocr.space/ocrapi]https://ocr.space/ocrapi[/ref]\n"
            "2. Click on 'Get API Key'\n"
            "3. Sign up for a free account\n"
            "4. Once registered, you'll receive your API key\n"
            "5. Copy and paste the key here\n\n"
            "The free tier includes:\n"
            "- 25,000 requests per month\n"
            "- Basic OCR features\n"
            "- Support for multiple languages"
        )
        
        info_label = Label(
            text=info_text,
            markup=True,
            size_hint_y=None,
            height=300,
            text_size=(400, None),
            halign='left',
            valign='top'
        )
        
        close_button = Button(
            text="Close",
            size_hint_y=None,
            height=40
        )
        
        content.add_widget(info_label)
        content.add_widget(close_button)
        
        popup = Popup(
            title='OCR API Key Information',
            content=content,
            size_hint=(None, None),
            size=(450, 400),
            auto_dismiss=False
        )
        
        close_button.bind(on_press=popup.dismiss)
        popup.open()
