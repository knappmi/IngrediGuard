from screens.base_screen import BaseScreen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger
# from opentelemetry import trace
from utils.error_handler import error_handler

class ResultsScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Results Screen for displaying filtered menu items."""
        # self.tracer = trace.get_tracer(__name__)
        Logger.info("[ResultsScreen] Initializing Results Screen")
        super().__init__(**kwargs)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.results_label = Label(
            text='Results will show here',
            markup=True,
            size_hint_y=None,
            size_hint_x=None,
            width=800,
            halign='left',
            valign='top',
            text_size=(800, None),
        )
        self.results_label.bind(
            texture_size=self.update_label_height,
            width=lambda inst, val: setattr(inst, "text_size", (val, None))
        )
        self.scroll.add_widget(self.results_label)

        self.layout.add_widget(self.scroll)
        self.add_back_button("allergy")

    @error_handler
    def update_label_height(self, instance, size):
        """Update the height of the label based on its texture size."""
        # with self.tracer.start_as_current_span("results_screen.update_label_height") as span:
        Logger.info("[ResultsScreen] Updating label height")
        self.results_label.height = size[1]

    @error_handler
    def on_pre_enter(self):
        """Display the filtered menu items when entering the screen."""
        # with self.tracer.start_as_current_span("results_screen.on_pre_enter") as span:
        #     span.set_attribute("manager_filtered_menu", self.manager.filtered_menu)

        Logger.info("[ResultsScreen] Displaying filtered menu items")
        Logger.debug("[ResultsScreen] Filtered menu data:", self.manager.filtered_menu)
        print("Filtered Menu Data:", self.manager.filtered_menu)
        menu_data = self.manager.filtered_menu
        self.results_label.text = ""

        if not menu_data:
            self.results_label.markup = True
            self.results_label.text = "[b]No menu items to display.[/b]"
            return

        safe_rows = [row for row in menu_data if row['is_safe']]
        unsafe_rows = [row for row in menu_data if not row['is_safe']]

        results_text = ""
        if safe_rows:
            results_text += "[b]No Allergens Found:[/b]\n"
            for row in safe_rows:
                item = row['item']
                results_text += f"  - {item}\n"
        
        if unsafe_rows:
            results_text += "[b]Better to Avoid (Contains Allergens):[/b]\n"
            for row in unsafe_rows:
                item = row['item']
                reasons = ", ".join(row.get('offending', []))
                # Softer red color and clearer text
                results_text += f"  - [color=ff6666]{item}[/color] (contains {reasons})\n"

        self.results_label.markup = True
        self.results_label.text = results_text