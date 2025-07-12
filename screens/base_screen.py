from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.logger import Logger
from utils.error_handler import error_handler

class BaseScreen(Screen):
    """Abstract base class for screens with shared layout helpers."""
    def __init__(self, **kwargs):
        """Initialize the base screen with a BoxLayout and a status label."""
        Logger.info(f"BaseScreen: Initializing {self.__class__.__name__}")
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.status_label = Label(text='', size_hint_y=None, height=30)
        self.layout.add_widget(self.status_label)
        self.add_widget(self.layout)

    @error_handler
    def set_status(self, text):
        """Set the text of the shared status label."""
        Logger.info(f"BaseScreen: Setting status: {text}")
        self.status_label.text = text

    @error_handler
    def add_back_button(self, target_screen):
        """Add a back button that switches to the given screen."""
        Logger.info(f"BaseScreen: Adding back button to {target_screen}")
        btn = Button(text='Back', size_hint_y=None, height=40)
        btn.bind(on_press=lambda _: setattr(self.manager, 'current', target_screen))
        self.layout.add_widget(btn)

    @error_handler
    def on_leave(self):
        """Clear the status label when leaving the screen."""
        Logger.info(f"BaseScreen: Leaving {self.__class__.__name__}")
        self.set_status('')
