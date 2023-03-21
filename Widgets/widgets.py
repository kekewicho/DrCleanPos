from utils import (
    MDCard,
    Builder,
    MapMarkerPopup
)
Builder.load_file('Widgets\widgets.kv')

class BtnServicio(MDCard):
    pass

class ActivosCard(MDCard):
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

