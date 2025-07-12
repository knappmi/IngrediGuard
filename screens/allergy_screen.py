from screens.base_screen import BaseScreen
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger
from utils.error_handler import error_handler
from utils.allergy_filter import perform_allergy_filter

class AllergyScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Screen for filtering menu items based on allergens."""
        Logger.info("[AllergyScreen] Initializing Allergy Screen")
        super().__init__(**kwargs)

        self.layout.add_widget(Label(
            text='Tell me what to watch out for.\n(e.g., "peanut", "milk, soy", etc.)',
            markup=True,
            height=80,
            size_hint_y=None,
            halign='center',
            valign='middle'
        ))
        self.allergen_input = TextInput(hint_text='Type allergen(s)...', multiline=False)
        self.layout.add_widget(self.allergen_input)

        self.filter_button = Button(text='Show Safe Dishes')
        self.filter_button.bind(on_press=self.filter_menu)
        self.layout.add_widget(self.filter_button)

        self.admin_btn = Button(text="Admin Tools", size_hint_y=None, height=40)
        self.admin_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_hub'))

        self.add_back_button("landing")

    @error_handler
    def on_pre_enter(self):
        """Check if the user is an admin and update the layout accordingly."""
        Logger.info("[AllergyScreen] Checking admin status")
        if self.manager.is_admin:
            if self.admin_btn not in self.layout.children:
                self.layout.add_widget(self.admin_btn, index=len(self.layout.children) - 1)
        else:
            if self.admin_btn in self.layout.children:
                self.layout.remove_widget(self.admin_btn)

    @error_handler
    def filter_menu(self, instance):
        """
        UI-facing method that gathers data and calls the core filtering logic.
        """
        Logger.info("[AllergyScreen] Filtering menu based on allergens")
        allergen_input = self.allergen_input.text.lower().strip()
        menu_data = self.manager.menu_data

        filtered_menu = perform_allergy_filter(menu_data, allergen_input)

        if filtered_menu is None:
            self.set_status("Please enter at least one allergen.")
            return

        self.manager.filtered_menu = filtered_menu
        self.manager.current = 'results'


    def on_leave(self):
        self.allergen_input.text = ""



