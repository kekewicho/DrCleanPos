from kivymd.uix.screen import Screen
from Widgets.widgets import ActivosCard

class ActivosScreen(Screen):
    def add_card(self):
        self.ids.ly.add_widget(ActivosCard())