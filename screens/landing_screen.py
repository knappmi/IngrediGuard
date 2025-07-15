from screens.base_screen import BaseScreen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger
# from opentelemetry import trace
from utils.error_handler import error_handler
from version import get_version

class LandingScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Landing Screen for the application."""
        # self.tracer = trace.get_tracer(__name__)
        Logger.info("[LandingScreen] Initializing Landing Screen")
        super().__init__(**kwargs)

        self.title = Label(text="Welcome to IngrediGuard", font_size='24sp', size_hint_y=None, height=50)
        self.layout.add_widget(self.title)

        self.parse_button = Button(text="Check Menu for Allergens", size_hint_y=None, height=50)
        self.parse_button.bind(on_press=lambda x: self.go_to_allergy())
        self.layout.add_widget(self.parse_button)

        self.admin_button = Button(text="Admin Tools", size_hint_y=None, height=50)
        self.admin_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_hub'))

        # Add version label at the bottom of the screen
        self.version_label = Label(
            text=f"Version {get_version()}",
            font_size='14sp',
            size_hint_y=None,
            height=30,
            color=(0.7, 0.7, 0.7, 1)  # Light gray
        )
        self.layout.add_widget(self.version_label)

        self.add_logout_button("login")

    @error_handler
    def on_pre_enter(self):
        """Check if the user is an admin and update the layout accordingly."""
        # with self.tracer.start_as_current_span("landing_screen.on_pre_enter") as span:
        #     span.set_attribute("manager_is_admin", self.manager.is_admin)

        Logger.info("[LandingScreen] Checking admin status")
        if self.manager.is_admin:
            Logger.info("[LandingScreen] User is admin, adding admin button")
            if self.admin_button not in self.layout.children:
                self.layout.add_widget(self.admin_button, index=2)
        else:
            Logger.info("[LandingScreen] User is not admin, removing admin button")
            if self.admin_button in self.layout.children:
                self.layout.remove_widget(self.admin_button)

    @error_handler
    def go_to_allergy(self):
        """Navigate to the allergy screen or upload menu if no menu is found."""
        # with self.tracer.start_as_current_span("landing_screen.go_to_allergy") as span:
        #     span.set_attribute("manager_menu_data", self.manager.menu_data)
        #     span.set_attribute("manager_is_admin", self.manager.is_admin)

        if not self.manager.menu_data:
            Logger.info("[LandingScreen] No menu data found, navigating to upload screen")
            if self.manager.is_admin:
                self.manager.current = 'upload'
            else:
                Logger.error("[LandingScreen] User is not admin and menu is empty, raising error")
                self.set_status("No menu has been uploaded. Please contact an administrator.")
        else:
            Logger.info("[LandingScreen] Menu data found, navigating to allergy screen")
            self.manager.current = 'allergy'