from utils import (
    Screen,
    Builder
)

Builder.load_file('Screens\MainScreen\MainScreen.kv')

class MainScreen(Screen):
    def loading(self):
        spinner=self.ids.spinner
        print(spinner.active)
        if spinner.active==True:spinner.active=False
        else:spinner.active=True