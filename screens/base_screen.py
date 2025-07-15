from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.logger import Logger
from utils.error_handler import error_handler
from kivy.uix.popup import Popup
from kivy.metrics import dp

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

    @error_handler
    def add_logout_button(self, target_screen='login'):
        """Add a logout button with confirmation that returns to the login screen.
        
        Args:
            target_screen: The screen to navigate to after logout (default: 'login')
        """
        Logger.info(f"Calling add_logout_button on {self.__class__.__name__}")
        btn = Button(
            text='Log Out', 
            size_hint_y=None, 
            height=40, 
            background_color=(0.9, 0.3, 0.3, 1.0)
        )
        btn.bind(on_press=self.show_logout_confirmation)
        self.layout.add_widget(btn)
        
    @error_handler
    def show_logout_confirmation(self, instance):
        """Show confirmation popup before logging out."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        content.add_widget(Label(
            text="Are you sure you want to log out?",
            halign='center'
        ))
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        cancel_btn = Button(text="Cancel")
        confirm_btn = Button(text="Log Out", background_color=(0.9, 0.3, 0.3, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title="Confirm Logout",
            content=content,
            size_hint=(0.7, 0.3),
            auto_dismiss=True
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.logout(popup))
        
        popup.open()
        
    @error_handler
    def logout(self, popup):
        """Log out the user and return to the login screen."""
        popup.dismiss()
        
        # Reset user info in the screen manager
        if hasattr(self.manager, 'current_user'):
            self.manager.current_user = None
        self.manager.is_admin = False
        
        # Return to login screen
        self.manager.current = 'login'
