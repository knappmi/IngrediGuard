from screens.base_screen import BaseScreen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
# from opentelemetry import trace
from utils.error_handler import error_handler

class LoginScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Login Screen for user authentication."""
        # self.tracer = trace.get_tracer(__name__)
        Logger.info("[LoginScreen] Initializing Login Screen")
        super().__init__(**kwargs)
        
        main_layout = FloatLayout()

        login_container = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(30), dp(30), dp(30), dp(30)],
            size_hint=(None, None),
            width=dp(500),
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
        username = self.username_input.text.strip().lower()
        password = self.password_input.text.strip()

        if username == "admin" and password == "P@ssw0rd":
            Logger.info("[LoginScreen] Admin login successful")
            self.status_label.text = "Welcome, Admin!"
            self.manager.is_admin = True
            self.manager.current = "landing"
        elif username == "user" and password == "P@ssw0rd":
            Logger.info("[LoginScreen] User login successful")
            self.status_label.text = f"Welcome, {username}!"
            self.manager.is_admin = False
            self.manager.current = "landing"
        else:
            self.status_label.text = "Invalid login. Please try again."


    def on_leave(self):
        self.username_input.text = ""
        self.password_input.text = ""
        self.status_label.text = ""
