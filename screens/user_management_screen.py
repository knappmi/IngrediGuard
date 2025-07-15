from screens.base_screen import BaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.logger import Logger
from models.user_database import UserDatabase
from utils.error_handler import error_handler

class UserManagementScreen(BaseScreen):
    def __init__(self, **kwargs):
        """User Management Screen for creating and managing users."""
        Logger.info("Initializing User Management Screen")
        super().__init__(**kwargs)

        # Create user database
        self.user_db = UserDatabase()
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Add user section
        self.add_user_section()
        
        # User list section with ScrollView
        self.add_user_list_section()
        
        # Bottom buttons
        bottom_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Reset database button (in red)
        reset_button = Button(
            text="Reset User Database", 
            background_color=(1, 0.3, 0.3, 1),
            size_hint_x=None,
            width=dp(200)
        )
        reset_button.bind(on_press=self.confirm_reset_database)
        
        # Back button
        back_button = Button(text="Back to Admin Hub")
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_hub'))
        
        bottom_buttons.add_widget(reset_button)
        bottom_buttons.add_widget(back_button)
        
        self.main_layout.add_widget(bottom_buttons)
        self.add_widget(self.main_layout)
        
        # Load initial user list
        self.refresh_user_list()

    def add_user_section(self):
        """Add the section for creating new users."""
        add_user_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200), spacing=dp(10))
        
        # Title
        add_user_box.add_widget(Label(
            text="Add New User",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30),
            bold=True
        ))
        
        # Form layout
        form_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Username field
        form_layout.add_widget(Label(text="Username:", halign='right', size_hint_x=0.3))
        self.username_input = TextInput(multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.username_input)
        
        # Password field
        form_layout.add_widget(Label(text="Password:", halign='right', size_hint_x=0.3))
        self.password_input = TextInput(multiline=False, password=True, size_hint_x=0.7)
        form_layout.add_widget(self.password_input)
        
        # Admin checkbox (implemented as a button for simplicity)
        form_layout.add_widget(Label(text="Admin:", halign='right', size_hint_x=0.3))
        self.admin_button = Button(text="No", background_color=(0.7, 0.7, 0.7, 1), size_hint_x=0.7)
        self.admin_button.is_admin = False
        self.admin_button.bind(on_press=self.toggle_admin_button)
        form_layout.add_widget(self.admin_button)
        
        add_user_box.add_widget(form_layout)
        
        # Add user button
        add_button = Button(
            text="Add User",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        add_button.bind(on_press=self.add_user)
        add_user_box.add_widget(add_button)
        
        self.main_layout.add_widget(add_user_box)

    def add_user_list_section(self):
        """Add the section for listing and managing users."""
        user_list_box = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Title
        user_list_box.add_widget(Label(
            text="User Management",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30),
            bold=True
        ))
        
        # User list with scroll view
        self.user_list_layout = GridLayout(
            cols=5, 
            spacing=dp(5),
            size_hint_y=None,
            row_default_height=dp(40),
            row_force_default=True
        )
        self.user_list_layout.bind(minimum_height=self.user_list_layout.setter('height'))
        
        # Headers with column width hints
        self.user_list_layout.add_widget(Label(text="Username", bold=True, size_hint_y=None, height=dp(40), size_hint_x=0.2))
        self.user_list_layout.add_widget(Label(text="Admin", bold=True, size_hint_y=None, height=dp(40), size_hint_x=0.15))
        self.user_list_layout.add_widget(Label(text="Status", bold=True, size_hint_y=None, height=dp(40), size_hint_x=0.15))
        self.user_list_layout.add_widget(Label(text="Toggle Admin", bold=True, size_hint_y=None, height=dp(40), size_hint_x=0.25))
        self.user_list_layout.add_widget(Label(text="Toggle Status", bold=True, size_hint_y=None, height=dp(40), size_hint_x=0.25))
        
        # Create scroll view with a fixed height that will expand to fill available space
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(10)
        )
        scroll_view.add_widget(self.user_list_layout)
        user_list_box.add_widget(scroll_view)
        
        self.main_layout.add_widget(user_list_box)

    @error_handler
    def toggle_admin_button(self, instance):
        """Toggle the admin button state."""
        instance.is_admin = not instance.is_admin
        if instance.is_admin:
            instance.text = "Yes"
            instance.background_color = (0.3, 0.7, 0.3, 1)  # Green
        else:
            instance.text = "No"
            instance.background_color = (0.7, 0.7, 0.7, 1)  # Gray

    @error_handler
    def add_user(self, instance):
        """Add a new user to the database."""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        is_admin = self.admin_button.is_admin
        
        if not username or not password:
            self.show_message("Error", "Username and password are required")
            return
            
        success, message = self.user_db.add_user(username, password, is_admin)
        
        if success:
            # Clear the form
            self.username_input.text = ""
            self.password_input.text = ""
            self.admin_button.is_admin = False
            self.admin_button.text = "No"
            self.admin_button.background_color = (0.7, 0.7, 0.7, 1)
            
            # Refresh the user list
            self.refresh_user_list()
            
        self.show_message("Add User", message)

    @error_handler
    def refresh_user_list(self):
        """Refresh the user list display."""
        # Clear existing widgets except headers (first 5)
        for i in range(len(self.user_list_layout.children) - 5):
            self.user_list_layout.remove_widget(self.user_list_layout.children[0])
        
        # Get updated user list
        users = self.user_db.get_users()
        
        # Add user rows
        for user in users:
            # Username
            self.user_list_layout.add_widget(Label(
                text=user['username'],
                size_hint_y=None,
                height=dp(40),
                size_hint_x=0.2
            ))
            
            # Admin status
            admin_label = Label(
                text="Yes" if user['is_admin'] else "No",
                size_hint_y=None,
                height=dp(40),
                size_hint_x=0.15,
                color=(0.3, 0.7, 0.3, 1) if user['is_admin'] else (0.7, 0.7, 0.7, 1)
            )
            self.user_list_layout.add_widget(admin_label)
            
            # Active status
            status_label = Label(
                text="Active" if user['is_active'] else "Disabled",
                size_hint_y=None,
                height=dp(40),
                size_hint_x=0.15,
                color=(0.3, 0.7, 0.3, 1) if user['is_active'] else (1, 0.3, 0.3, 1)
            )
            self.user_list_layout.add_widget(status_label)
            
            # Toggle admin button
            admin_btn = Button(
                text="Make Admin" if not user['is_admin'] else "Remove Admin",
                size_hint_y=None,
                height=dp(40),
                size_hint_x=0.25,
                font_size=dp(13)
            )
            admin_btn.user_id = user['id']
            admin_btn.is_admin = not user['is_admin']  # The opposite of current state
            admin_btn.bind(on_press=self.toggle_user_admin)
            self.user_list_layout.add_widget(admin_btn)
            
            # Toggle status button
            status_btn = Button(
                text="Disable" if user['is_active'] else "Enable",
                size_hint_y=None,
                height=dp(40),
                size_hint_x=0.25,
                font_size=dp(13),
                background_color=(1, 0.5, 0.5, 1) if user['is_active'] else (0.5, 1, 0.5, 1)
            )
            status_btn.user_id = user['id']
            status_btn.make_active = not user['is_active']  # The opposite of current state
            status_btn.bind(on_press=self.toggle_user_status)
            self.user_list_layout.add_widget(status_btn)

    @error_handler
    def toggle_user_admin(self, instance):
        """Toggle a user's admin status."""
        success, message = self.user_db.toggle_user_admin(instance.user_id, instance.is_admin)
        
        if success:
            self.refresh_user_list()
            
        self.show_message("User Management", message)

    @error_handler
    def toggle_user_status(self, instance):
        """Toggle a user's active status."""
        success, message = self.user_db.toggle_user_status(instance.user_id, instance.make_active)
        
        if success:
            self.refresh_user_list()
            
        self.show_message("User Management", message)

    @error_handler
    def confirm_reset_database(self, instance):
        """Show confirmation popup before resetting the database."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        content.add_widget(Label(
            text="WARNING: This will delete all users and reset to default admin.\nThis action cannot be undone!",
            halign='center'
        ))
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        cancel_btn = Button(text="Cancel")
        confirm_btn = Button(text="Reset Database", background_color=(1, 0.3, 0.3, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title="Confirm Database Reset",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.reset_database(popup))
        
        popup.open()

    @error_handler
    def reset_database(self, popup):
        """Reset the user database."""
        popup.dismiss()
        
        success, message = self.user_db.reset_database()
        
        if success:
            self.refresh_user_list()
            
        self.show_message("Database Reset", message)

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
