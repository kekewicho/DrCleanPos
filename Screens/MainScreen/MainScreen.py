from utils import (
    Screen,
    Builder,
    bd
)

Builder.load_file('Screens\MainScreen\MainScreen.kv')

class MainScreen(Screen):
    dataStream=None

    def loading(self):
        spinner=self.ids.spinner
        if spinner.active==True:spinner.active=False
        else:spinner.active=True
       
    def startStreaming(self):
        daFunction=self.ids.main_manager.get_screen('Activos_Screen').eventListener
        self.dataStream=bd.child('notas').stream(daFunction)
