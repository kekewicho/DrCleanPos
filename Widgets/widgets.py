from utils import (
    MDCard,
    Builder,
    MapMarkerPopup,
    StringProperty,
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    MDBoxLayout
)
Builder.load_file('Widgets\widgets.kv')

class BtnServicio(MDCard):
    pass

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
    detalles_domicilio = {}

    def __init__(self,lat,lon,detalles_domicilio,*args):
        super().__init__(*args)
        self.detalles_domicilio=detalles_domicilio
        self.lat=lat
        self.lon=lon
        self.source='Assets\images\map_marker.png'

    def on_release(self):
        pass
        # Open up the LocationPopupMenu
        #menu = LocationPopupMenu(self.market_data)
        #menu.size_hint = [.8, .9]
        #menu.open()

