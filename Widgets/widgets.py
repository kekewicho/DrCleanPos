from utils import (
    MDCard,
    Builder,
    MapMarkerPopup,
    StringProperty,
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    MDBoxLayout,
    MDDropdownMenu,
    dp,
    get_app,
    Clipboard,
    MDSnackbar,
    MDLabel
)
Builder.load_file('Widgets\widgets.kv')

class BtnServicio(MDCard):
    service=StringProperty()
    costo=NumericProperty()

    def __init__(self,servicio:str,costo:float,*args):
        super().__init__(*args)
        self.service=servicio.replace('-',' / ')
        self.costo=costo

class ActivosCard(MDCard):
    id_nota=StringProperty()
    status=StringProperty()
    aDomicilio=BooleanProperty()
    content=ObjectProperty()
    fecha=None

    status_config={
        'recoleccion':{
            'color':'#089cba',
            'icon':'truck'
            },
        'sucursal':{
            'color':'#044B59',
            'icon':'store-check'
            },
        'entrega':{
            'color':'#a1c04e',
            'icon':'check'
            },
    }

    def __init__(self,idNota:str,userName:str,status:str,fecha,aDomicilio:bool,total:float=0.00,saldo:float=0.00,*args,):
        super().__init__(*args,)
        self.id_nota=idNota
        self.status=status
        self.aDomicilio=aDomicilio
        self.fecha=fecha

        self.setStatus(status)
        self.ids.user_name.text=userName
        self.ids.aDomicilio.text='En sucursal' if aDomicilio else 'A domicilio'
        self.ids.fecha.text=fecha

        if total==0.00:
            self.add_widget(ContentNoCargada())
        else:
            self.content=ContentCargada(total=total,saldo=saldo)
            self.add_widget(
                self.content
            )

    def setStatus(self,status):
        config=self.status_config.get(status)
        self.ids.statusIcon.md_bg_color=config['color']
        self.ids.statusIcon.icon=config['icon']
        self.status=status

class ContentCargada(MDBoxLayout):
    total=NumericProperty()
    saldo=NumericProperty()

    def __init__(self,total:float,saldo:float, *args):
        super().__init__(*args)
        self.total=total
        self.saldo=saldo

        self.ids.total.text='{:,.2f}'.format(total)
        self.ids.saldo.text='{:,.2f}'.format(saldo)

class ContentNoCargada(MDBoxLayout):
    pass

class DomicilioMarker(MapMarkerPopup):
    detalles_domicilio = StringProperty()

    def __init__(self,lat,lon,detalles_domicilio,*args):
        super().__init__(*args)
        self.detalles_domicilio=detalles_domicilio
        self.lat=lat
        self.lon=lon
        self.source='Assets\images\map_marker.png'

    def on_release(self):
        # Open up the LocationPopupMenu
        menu_items = [
            {
                "text": 'Copiar datos',
                "viewclass": "OneLineListItem",
                "height":dp(56),
                "on_release":lambda x=self.detalles_domicilio:self.copiar_datos()
            },
            {
                "text": 'Eliminar',
                "viewclass": "OneLineListItem",
                "height":dp(56),
                "on_release":lambda x=self:get_app().root.ids.main_manager.get_screen('Clientes_Screen').delete_address(x)
            }
        ]
        self.menu = LocationMenu(
            domicilio=self.detalles_domicilio,
            caller=self,
            items=menu_items,
            width_mult=3,
            position="top",
            ver_growth="up"
        )
        self.menu.open()
    
    def copiar_datos(self):
        root=get_app().root.ids.main_manager.get_screen('Clientes_Screen')
        cliente=root.ids.nombre.text+' '+root.ids.apellido.text
        text=f"Te comparto el domicilio de {cliente}\nDomicilio: {self.detalles_domicilio}\nGoogle Maps: https://www.google.com/maps?q={self.lat},{self.lon}"
        Clipboard.copy(text)
        MDSnackbar(MDLabel(text='¡Información copiada el portapapeles!',theme_text_color="Custom",
                text_color="#ffffff",)).open()


class LocationMenu(MDDropdownMenu):
    def __init__(self,domicilio,**args):
        super().__init__(**args)
        

