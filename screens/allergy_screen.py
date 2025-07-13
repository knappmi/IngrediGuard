from screens.base_screen import BaseScreen
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.logger import Logger
from utils.error_handler import error_handler
from utils.allergy_filter import perform_allergy_filter, ALLERGEN_MAP

class AllergyScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Screen for filtering menu items based on allergens."""
        Logger.info("[AllergyScreen] Initializing Allergy Screen")
        super().__init__(**kwargs)

        # Add a spacer at the top to center content better
        self.layout.add_widget(Widget(size_hint_y=None, height=20))

        self.layout.add_widget(Label(
            text='Tell me what to watch out for.\n(e.g., "peanut", "milk, soy", etc.)',
            markup=True,
            height=50,  # Reduced from 60 to 50
            size_hint_y=None,
            halign='center',
            valign='middle'
        ))
        
        # Reduce space between label and input
        self.layout.add_widget(Widget(size_hint_y=None, height=5))
        
        # Input field with limited width
        input_wrapper = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50  # Increased from 40 to 50
        )
        
        self.allergen_input = TextInput(
            hint_text='Type allergen(s)...',
            multiline=False,
            size_hint_x=0.8,  # Increased from 0.7 to 0.8
            size_hint_y=None,
            height=40,  # Increased from 30 to 40
            pos_hint={'center_x': 0.5},
            font_size=18  # Added font size for better readability
        )
        
        input_wrapper.add_widget(self.allergen_input)
        self.layout.add_widget(input_wrapper)

        # Add a label for quick filters
        self.layout.add_widget(Label(
            text='Common Allergens:',
            size_hint_y=None,
            height=30,
            halign='center'
        ))
        
        # Create scrollview for allergen quick filters
        quick_filters_scroll = ScrollView(
            size_hint_y=None,
            height=140  # Slightly increased height for better visibility
        )
        
        # Use a grid layout for the quick filter buttons
        quick_filters_grid = GridLayout(
            cols=3,  # 3 buttons per row
            spacing=8,  # Increased spacing
            padding=8,
            size_hint_y=None
        )
        quick_filters_grid.bind(minimum_height=quick_filters_grid.setter('height'))
        
        # Add buttons for common allergens - prioritize most common allergens first
        common_allergens = ['peanut', 'milk', 'egg', 'soy', 'wheat', 'tree nut', 'fish', 'shellfish', 'sesame']
        # Add remaining allergens
        remaining_allergens = [a for a in ALLERGEN_MAP.keys() if a not in common_allergens]
        all_allergens = common_allergens + remaining_allergens
        
        for allergen in all_allergens:
            # Create a button for each allergen
            allergen_btn = Button(
                text=allergen.title(),  # Capitalize the allergen name
                size_hint_y=None,
                height=40,
                background_normal='',  # Remove default background
                background_color=(0.3, 0.6, 0.9, 1.0),  # Light blue color
                color=(1, 1, 1, 1),  # White text
                font_size=16  # Larger font
            )
            
            # Create a callback that adds this allergen to the input
            def create_allergen_callback(allergen_name):
                def callback(instance):
                    current_text = self.allergen_input.text.strip()
                    if current_text:
                        # If there's already text, append with a comma
                        self.allergen_input.text = f"{current_text}, {allergen_name}"
                    else:
                        # Otherwise just set the text
                        self.allergen_input.text = allergen_name
                return callback
            
            allergen_btn.bind(on_press=create_allergen_callback(allergen))
            quick_filters_grid.add_widget(allergen_btn)
        
        quick_filters_scroll.add_widget(quick_filters_grid)
        self.layout.add_widget(quick_filters_scroll)
        
        # Add some space between quick filters and the main filter button
        self.layout.add_widget(Widget(size_hint_y=None, height=10))

        # Button for filtering - slightly larger
        button_wrapper = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,  # Reduced from 70 to 60
            padding=[0, 10, 0, 0]  # Reduced top padding from 15 to 10
        )
        
        self.filter_button = Button(
            text='Show Safe Dishes',
            size_hint=(0.8, None),  # 80% of the width
            height=50,              # Slightly taller
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.filter_button.bind(on_press=self.filter_menu)
        
        button_wrapper.add_widget(self.filter_button)
        self.layout.add_widget(button_wrapper)
        
        # Add flexible space to push admin and back buttons to the bottom
        # Use a smaller flexible space since we've added quick filters
        self.layout.add_widget(Widget(size_hint_y=0.3))

        # Create admin button but don't add it yet (will be added in on_pre_enter if admin)
        self.admin_btn = Button(text="Admin Tools", size_hint_y=None, height=40)
        self.admin_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_hub'))

        # Add back button at the bottom
        back_btn = Button(text="Back", size_hint_y=None, height=40)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'landing'))
        self.layout.add_widget(back_btn)

    @error_handler
    def on_pre_enter(self):
        """Check if the user is an admin and update the layout accordingly."""
        Logger.info("[AllergyScreen] Checking admin status")
        
        # Always make sure admin button is removed first to prevent duplicates
        if self.admin_btn in self.layout.children:
            self.layout.remove_widget(self.admin_btn)
            
        # Add admin button above back button if user is admin
        if self.manager.is_admin:
            # Insert before the last item (back button)
            self.layout.add_widget(self.admin_btn, index=len(self.layout.children) - 1)

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



