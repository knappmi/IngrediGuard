from screens.base_screen import BaseScreen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp
# from opentelemetry import trace
from utils.error_handler import error_handler
from models.user_database import UserDatabase

class LoginScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Login Screen for user authentication."""
        # self.tracer = trace.get_tracer(__name__)
        Logger.info("[LoginScreen] Initializing Login Screen")
        super().__init__(**kwargs)
        
        # Initialize user database
        self.user_db = UserDatabase()
        
        main_layout = FloatLayout()

        login_container = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(30), dp(30), dp(30), dp(30)],
            size_hint=(None, None),
            width=dp(350),  # Reduced from 500 to 350
            height=dp(400),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        title_label = Label(
            text="[b]Welcome to IngrediGuard![/b]",
            font_size=dp(32),
            markup=True,
            size_hint_y=None,
            height=dp(70)
        )
        login_container.add_widget(title_label)

        username_layout = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(90))
        username_layout.add_widget(Label(
            text="Username", 
            halign="left", 
            size_hint_y=None, 
            height=dp(25), 
            font_size=dp(18)
        ))
        self.username_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )
        username_layout.add_widget(self.username_input)
        login_container.add_widget(username_layout)

        password_layout = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(90))
        password_layout.add_widget(Label(
            text="Password", 
            halign="left", 
            size_hint_y=None, 
            height=dp(25), 
            font_size=dp(18)
        ))
        self.password_input = TextInput(
            password=True, 
            multiline=False, 
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )
        password_layout.add_widget(self.password_input)
        login_container.add_widget(password_layout)

        button_layout = BoxLayout(
            orientation="horizontal", 
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(70), 
            padding=[0, dp(20), 0, 0]
        )
        
        login_button = Button(
            text="Login",
            font_size=dp(18),
            size_hint=(0.7, None),
            height=dp(50),
            pos_hint={'center_x': 0.5}
        )
        login_button.bind(on_press=self.login)
        button_layout.add_widget(login_button)
        login_container.add_widget(button_layout)
        
        # Add Reset App button
        reset_button_layout = BoxLayout(
            orientation="horizontal", 
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(50)
        )
        
        # Spacer to push reset button to the right
        spacer = BoxLayout(size_hint_x=0.7)
        reset_button_layout.add_widget(spacer)
        
        # Reset App button
        reset_app_button = Button(
            text="Reset App",
            font_size=dp(14),
            size_hint=(0.3, None),
            height=dp(40),
            background_color=(0.9, 0.3, 0.3, 1.0),
        )
        reset_app_button.bind(on_press=self.show_reset_popup)
        reset_button_layout.add_widget(reset_app_button)
        
        login_container.add_widget(reset_button_layout)

        self.status_label = Label(
            text="", 
            size_hint_y=None, 
            height=dp(40), 
            font_size=dp(16)
        )
        login_container.add_widget(self.status_label)

        main_layout.add_widget(login_container)
        self.layout.add_widget(main_layout)

    @error_handler
    def login(self, instance):
        """Handle the login process."""
        # with self.tracer.start_as_current_span("login_screen.login") as span:
        Logger.info("[LoginScreen] Attempting to log in")
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.status_label.text = "Please enter username and password"
            return

        success, message, user_info = self.user_db.authenticate_user(username, password)
        
        if success:
            Logger.info(f"[LoginScreen] {username} login successful")
            self.status_label.text = f"Welcome, {username}!"
            self.manager.is_admin = user_info['is_admin']
            self.manager.current_user = user_info
            self.manager.current = "landing"
        else:
            self.status_label.text = message
            
    @error_handler
    def show_reset_popup(self, instance):
        """Show the reset confirmation popup."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        content.add_widget(Label(
            text="WARNING: This will reset all users and app data!\nDefault login will be:\nUsername: admin\nPassword: admin123",
            halign='center'
        ))
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        cancel_btn = Button(text="Cancel")
        confirm_btn = Button(text="Reset App", background_color=(1, 0.3, 0.3, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title="Reset Application",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.reset_app(popup))
        
        popup.open()
        
    @error_handler
    def reset_app(self, popup):
        """Reset the entire application."""
        popup.dismiss()
        
        # Reset user database
        success, message = self.user_db.reset_database()
        
        # Reset other databases if needed
        # For example: MenuDatabase().reset_database()
        
        if success:
            self.show_message("Application Reset", "Application has been reset. Please login with default credentials.")
            self.username_input.text = ""
            self.password_input.text = ""
        else:
            self.show_message("Reset Failed", message)
            
    def show_message(self, title, message):
        """Show a popup message."""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message))
        button = Button(text="OK", size_hint_y=None, height=dp(40))
        content.add_widget(button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.3),
            auto_dismiss=True
        )
        
        button.bind(on_press=popup.dismiss)
        popup.open()


    def on_leave(self):
        self.username_input.text = ""
        self.password_input.text = ""
        self.status_label.text = ""
