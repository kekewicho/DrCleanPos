from utils import (
    Screen,
    Animation
)

from Widgets.widgets import ActivosCard

class ActivosScreen(Screen):
    def selector(self,pos):
        anim=Animation(size_hint=(0,0),duration=.1)+Animation(pos_hint={'center_x':pos},duration=.05)+Animation(size_hint=(.185,.8),duration=.2)
        anim.start(self.ids.selector)
    
    def add_card(self):
        self.ids.ly.add_widget(ActivosCard())
