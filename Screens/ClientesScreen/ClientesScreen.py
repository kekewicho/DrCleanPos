from utils import (
    os,
    requests,
    Screen,
    bd,
    OneLineListItem,
    MDTextField,
    MDRaisedButton,
    MDSnackbar,
    MDLabel,
    MDBoxLayout,
    MapMarkerPopup,
    mainthread,
    clientes,
    Thread,
    MDIconButton,
)

from Widgets.widgets import DomicilioMarker

api_key=os.getenv("MAPS_API_KEY")

# URL de la API de Autocompletar
url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

class LayoutSD(MDBoxLayout):
    def remove(self):
        self.parent.remove_widget(self)

class ClientesScreen(Screen):
    layout=None
    markers_list=[]
    search_marker=None

    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout=LayoutSD()

    #Busqueda consulta inicial de los clientes:
    def get_clientes(self):
        _clientes=bd.child('clientes').get()
        for i in _clientes.each():
            self.set_clientes(i)
            clientes[i.key()]=i.val()
    
    @mainthread
    def set_clientes(self,clientes):
        self.ids.clientes_list.add_widget(
            OneLineListItem(
                text=clientes.val()['nombre']+' '+clientes.val()['apellido'],
                on_release=lambda x, key=clientes.key(): self.set_state('view',key)
            )
        )


    #Funciones y atributos para el funcionamiento de la pantalla
    def add_address(self):
        self.markers_list.append(self.search_marker)
        self.clear_markers()
        self.set_markers(self.markers_list)
        self.ids.clientes_manager.current='detalles_cliente'
        self.search_marker=None

    def busqueda(self,text):
        if len(text)==0:
            self.ids.clientes_list.clear_widgets()
            for i in clientes:
                self.ids.clientes_list.add_widget(OneLineListItem(
                    text=clientes[i]['nombre']+' '+clientes[i]['apellido'],
                    on_release=lambda x, key=i: self.set_state('view',key)
                    )
                )
        if len(text)<3: return None
        self.ids.clientes_list.clear_widgets()
        for i in clientes:
            if str(i)==text or (text.upper() in clientes[i]['nombre'].upper()+' '+clientes[i]['apellido'].upper()):
                self.ids.clientes_list.add_widget(OneLineListItem(
                    text=clientes[i]['nombre']+' '+clientes[i]['apellido'],
                    on_release=lambda x, key=i: self.set_state('view',key)
                    )
                )
    
    def clean(self):
        for i in self.ids.datos.children:
            if isinstance(i,MDTextField):
                i.text=''
                i.disabled=True
        for i in self.ids.mapa_layout.children:
            if isinstance(i,MapMarkerPopup) or isinstance(i,LayoutSD):
                self.ids.mapa_layout.remove_widget(i)
        self.ids.mapa.zoom=12
        self.ids.mapa.center_on(22.763704, -102.555196)     
    
    def guardar_cambios(self):
        data=self.recabar_datos()
        if len(self.ids.id_user.text)==0:
            new_user=bd.child('clientes').push(data)
            userid=new_user['name']
            print(data)
            print(userid)
            clientes[userid]=data
            MDSnackbar(MDLabel(text='Cliente registrado con éxito',theme_text_color="Custom",
                text_color="#ffffff",)).open()
        else:
            bd.child(f'clientes/{self.ids.id_user.text}').update(data)
            MDSnackbar(MDLabel(text='Cliente actualizado con éxito',theme_text_color="Custom",
                text_color="#ffffff",)).open()
        self.clean()
        self.ids.clientes_manager.current='lista_clientes'
        self.ids.clientes_list.clear_widgets()
        Thread(target=self.get_clientes()).start()


    def eliminar(self):
        bd.child(f'clientes/{self.ids.id_user.text}').remove()
        clientes.pop(self.ids.id_user.text)
        self.clean()
        MDSnackbar(MDLabel(text='Cliente eliminado con éxito',theme_text_color="Custom",
                text_color="#ffffff",)).open()
        self.ids.clientes_manager.current="lista_clientes"
        self.ids.clientes_list.clear_widgets()
        Thread(target=self.get_clientes()).start()
    
    def define_ubi(self,id,details):
        print(id)
        global api_key,url
        # URL de la API de Detalles de Lugar
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        
        # Parámetros de la consulta de detalles
        details_params = {
            "place_id": id,
            "key": api_key
        }
        
        # Realizar la solicitud a la API de Detalles de Lugar
        details_response = requests.get(details_url, params=details_params)
        
        # Verificar si la solicitud tuvo éxito
        if details_response.status_code == 200:
            # Cargar la respuesta en un diccionario
            details_data = details_response.json()
            
            # Verificar si hay resultados en la respuesta
            if details_data["status"] == "OK":
                # Obtener las coordenadas de longitud y latitud del lugar
                location = details_data["result"]["geometry"]["location"]
                lat = location["lat"]
                lng = location["lng"]
        print(lat,lng)
        self.ids.mapa.center_on(lat, lng)
        self.ids.mapa.zoom=17
        if self.search_marker is None:
            marker=DomicilioMarker(lat=lat,lon=lng,detalles_domicilio={'domicilio':details})
            self.search_marker=marker
            self.ids.mapa.add_marker(self.search_marker)
        else:
            self.search_marker.lat,self.search_marker.lon=lat,lng
            self.search_marker.detalles_domicilio=details

    def clear_markers(self):
        for i in self.markers_list:self.ids.mapa.remove_marker(i)
    
    def set_markers(self,data):
        if len(data)==0:self.ids.mapa_layout.add_widget(self.layout);return None
        lat=0
        lon=0
        for i in data:
            self.ids.mapa.add_marker(i)
            lat+=i.lat
            lon+=i.lon
        lat_prom,lon_prom=lat/len(data),lon/len(data)
        self.ids.mapa.center_on(lat_prom, lon_prom)
        self.ids.mapa.zoom=12

    def show_sugest(self,data):
        data=self.get_ubi(data)
        self.ids.datos.clear_widgets()
        for i in data:
            id_value = i[1]  # Guarda el valor de 'data' en una variable
            self.ids.datos.add_widget(OneLineListItem(
                text=i[0],
                on_release=lambda _, id=id_value: self.define_ubi(id,i[0])
                ))


    def get_ubi(self,text):
        global api_key,url
        query = text
        # Parámetros de la consulta
        params = {
            "input": query,
            "key": api_key,
            "location":"22.76837837206175%2C-102.57307329268119"
        }

        # Realizar la solicitud a la API
        response = requests.get(url, params=params)

        # Verificar si la solicitud tuvo éxito
        if response.status_code == 200:
            # Cargar la respuesta en un diccionario
            data = response.json()
            
            # Verificar si hay resultados en la respuesta
            if data["status"] == "OK":
                # Imprimir los resultados con un índice
                res=[]
                for prediction in data["predictions"]:
                    res.append([prediction['description'],prediction['place_id']])
                for i in res:print(i)
                return res
    
    def set_state(self,state:str,user=''):
        flds=('id_user','nombre','apellido','telefono','rfc','domicilio_fiscal','razon_social','regimen_fiscal')
        self.ids.layout_btns.clear_widgets()
        
        if state=='nothing':
            self.ids.clientes_manager.current='lista_clientes'
        if state=='new':
            self.ids.clientes_manager.current='detalles_cliente'
            for i in flds:
                self.ids[i].text=''
                if i=='id_user':self.ids[i].disabled=True;continue
                self.ids[i].disabled=False
            self.ids.layout_btns.add_widget(MDIconButton(icon='content-save-all',on_release=lambda x:self.guardar_cambios()))
            self.ids.mapa_layout.add_widget(self.layout)
        if state=='edit':
            for i in flds:
                if i=='id_user':self.ids[i].disabled=True;continue
                self.ids[i].disabled=False
            self.ids.layout_btns.add_widget(MDIconButton(icon='content-save-all',on_release=lambda x:self.guardar_cambios()))
        if state=='view':
            self.ids.clientes_manager.current='detalles_cliente'
            for i in flds:
                self.ids[i].disabled=True
            user_id=user if not user=='' else self.ids.id_user.text
            user=bd.child('clientes/'+user).get()
            for i in ('id_user','nombre','apellido','telefono','rfc','domicilio_fiscal','razon_social','regimen_fiscal'):
                try:
                    if i=='id_user':self.ids.id_user.text=user_id
                    else:self.ids[i].text=(user.val()).get(i)
                except:
                    print(i)
            domicilio=(user.val()).get('domicilio')

            self.ids.layout_btns.add_widget(MDIconButton(icon='account-edit',on_release=lambda x:self.set_state('edit')))
            self.ids.layout_btns.add_widget(MDIconButton(icon='account-remove',on_release=lambda x:self.eliminar()))


            if domicilio is None or len(domicilio)==0:self.ids.mapa_layout.add_widget(self.layout);return None
            else:
                for i in domicilio:
                    pass
                    #address=DomicilioMarker(lat=domicilio[0]['lat'], lon=domicilio[0]['lon'],detalles_domicilio={'domicilio':})
                    #address=MapMarkerPopup(lat=domicilio[0]['lat'], lon=domicilio[0]['lon'],source='Assets\images\map_marker.png')
                    #self.ids.mapa.add_marker(address)
                    #self.markers_list.append(address)
            self.ids.mapa_layout.add_widget(MDRaisedButton(
                        text='Agregar domicilio',
                        md_bg_color='#089cba',
                        pos_hint={'right':.95,'top':.95}))
        if state=='add_adress':
            self.ids.clientes_manager.current='add_address'
            self.clear_markers()
            self.ids.mapa_layout.remove_widget(self.layout)



    def recabar_datos(self):
        data={}
        for i in ('regimen_fiscal','razon_social','domicilio_fiscal','rfc','telefono','apellido','nombre','id_user'):
            if not len(self.ids[i].text)==0:data[i]=self.ids[i].text
        addresses=[]
        if not len(self.markers_list)==0:
            for i in self.markers_list:
                address={}
                address['descripcion']=i.detalles_domicilio['domicilio']
                address['lat']=i.lat
                address['lon']=i.lon
                addresses.append(address)
        return data