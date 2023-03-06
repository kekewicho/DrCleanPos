#Es necesario usar este backend de Matplotlib para que no se redimensione la
#app al crear los graficos, ya que al parecer el que usa por defecto altera
#los DPI de la app
from utils import matplotlib
matplotlib.use('agg')

#Importando todas las clases de las pantallas
from Screens.MainScreen.MainScreen import MainScreen
from Screens.NotasScreen.NotasScreen import NotasScreen
from Screens.ClientesScreen.ClientesScreen import ClientesScreen
from Screens.ReportesScreen.ReportesScreen import ReportesScreen
from Screens.ActivosScreen.ActivosScreen import ActivosScreen
from Screens.VentaScreen.VentaScreen import VentaScreen

#Demás utilidades para el inicio de la app
from utils import (
    MDApp,
    Thread,
    os,
    LabelBase
)

class DrCleanPOS(MDApp):
    def build(self):
        return MainScreen()
    
    def on_start(self):
        Thread(target=self.root.ids.main_manager.get_screen('Venta_Screen').load_services).start()
        Thread(target=self.root.ids.main_manager.get_screen('Notas_Screen').load_data).start()
        Thread(target=self.root.ids.main_manager.get_screen('Clientes_Screen').get_clientes).start()

if __name__=='__main__':
    for i in os.listdir('Assets/fonts'):
        LabelBase.register(name=(i.replace('Lato-','')).replace('.ttf',''),fn_regular='Assets\\fonts\\'+i)
    DrCleanPOS().run()
    