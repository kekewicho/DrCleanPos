import os
import requests
from kivymd.uix.screen import Screen
import database as db
from kivymd.uix.list import OneLineListItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.garden.mapview.mapview.view import MapMarkerPopup
import database
from kivy.clock import mainthread

api_key=os.getenv("MAPS_API_KEY")
print(api_key)

# URL de la API de Autocompletar
url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

class LayoutSD(MDBoxLayout):
    pass

class Botones(MDRaisedButton):
    pass

class ClientesScreen(Screen):
    #Busqueda consulta inicial de los clientes:
    def get_clientes(self):
        clientes=database.bd.child('clientes').get()
        for i in clientes.each():
            self.set_clientes(i)
            database.clientes[i.key()]=i.val()
    
    @mainthread
    def set_clientes(self,clientes):
        self.ids.clientes_list.add_widget(
            OneLineListItem(
                text=clientes.val()['nombre']+' '+clientes.val()['apellido'],
                on_release=lambda x, key=clientes.key(): self.select_user(key)
            )
        )


    #Funciones y atributos para el funcionamiento de la pantalla
    def select_user(self,user):
        self.ids.clientes_manager.current='detalles_cliente'
        user_id=user
        user=db.bd.child('clientes/'+user).get()
        for i in ('id_user','nombre','apellido','telefono','rfc','domicilio_fiscal','razon_social','regimen_fiscal'):
            try:
                if i=='id_user':self.ids.id_user.text=user_id
                else:self.ids[i].text=(user.val()).get(i)
            except:
                print(i)
        domicilio=(user.val()).get('domicilio')
        if domicilio is None or len(domicilio)==0:self.ids.mapa_layout.add_widget(LayoutSD());return None
        if len(domicilio)==1:
            self.ids.mapa.center_on(domicilio[0]['lat'], domicilio[0]['lon'])
            self.ids.mapa.zoom=17
            self.ids.mapa.add_marker(MapMarkerPopup(lat=domicilio[0]['lat'], lon=domicilio[0]['lon'],source='Assets\images\map_marker.png'))
        if len(domicilio)>1:
            for i in domicilio:
                self.ids.mapa.zoom=17
                self.ids.mapa.add_marker(MapMarkerPopup(lat=domicilio[0]['lat'], lon=domicilio[0]['lon'],source='Assets\images\map_marker.png'))
        self.ids.mapa_layout.add_widget(MDRaisedButton(
                    text='Agregar domicilio',
                    md_bg_color='#089cba',
                    pos_hint={'right':.95,'top':.95}))

    def add_address(self):
        self.ids.clientes_manager.current='add_address'
        self.ids.mapa_layout.remove_widget(self.ids.mapa_layout.children[0])

    def busqueda(self,text):
        if len(text)<3: return None
        self.ids.clientes_list.clear_widgets()
        for i in db.clientes:
            if str(i)==text or (text.upper() in db.clientes[i]['nombre'].upper()+' '+db.clientes[i]['apellido'].upper()):
                self.ids.clientes_list.add_widget(OneLineListItem(
                    text=db.clientes[i]['nombre']+' '+db.clientes[i]['apellido'],
                    on_release=lambda x, key=i: self.select_user(key)
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
    
    def clean_filters(self):
        self.ids.clientes_list.clear_widgets()
        for i in db.clientes:
            self.ids.clientes_list.add_widget(OneLineListItem(
                text=db.clientes[i]['nombre']+' '+db.clientes[i]['apellido'],
                on_release=lambda x, key=i: self.select_user(key)
                )
            )
        self.ids.fldSearch.text=''

    
    def guardar_cambios(self):
        data={}
        for i in self.ids.datos.children:
            if isinstance(i,MDTextField) and not i.hint_text=='ID de usuario':
                if len(i.text)>0:data[list(self.ids.keys())[list(self.ids.values()).index(i)]]=i.text
        if len(self.ids.id_user.text)==0:
            new_user=db.bd.child('clientes').push(data)
            userid=new_user['name']
            print(userid)
            db.clientes[userid]=data
            MDSnackbar(MDLabel(text='Cliente registrado con éxito',theme_text_color="Custom",
                text_color="#ffffff",)).open()
        else:
            db.bd.child(f'clientes/{self.ids.id_user.text}').update(data)
            MDSnackbar(MDLabel(text='Cliente actualizado con éxito',theme_text_color="Custom",
                text_color="#ffffff",)).open()
        self.clean()


    def modificar(self):
        for i in self.ids.datos.children:
            if isinstance(i,MDTextField) and not i.hint_text=='ID de usuario':
                i.disabled=False
        for widget in self.ids.buttons_layout.children:
            if isinstance(widget,Botones):self.ids.buttons_layout.remove_widget(widget)
        for i in ('Cancelar','Guardar'):self.ids.buttons_layout.add_widget(Botones(text=i))

    def eliminar(self):
        db.bd.child(f'clientes/{self.ids.id_user.text}').remove()
        db.clientes.pop(self.ids.id_user.text)
        self.clean()
        MDSnackbar(MDLabel(text='Cliente eliminado con éxito',theme_text_color="Custom",
                text_color="#ffffff",)).open()
    
    def nuevo_usuario(self):
        if self.menu is None:self.menu = MDDropdownMenu(
            items=[],
            position="bottom",
            width_mult=6,
            )
        self.ids.clientes_manager.current='detalles_cliente'
        self.clean()
        fld=MDTextField(
            mode='round',
            icon_left='magnify',
            hint_text='Buscar domicilio',
            pos_hint={'x':.05,'top':.95},
            fill_color_normal=(1,1,1,1),
            size_hint_x=.7
            )
        self.menu.caller=fld
        fld.bind(on_text_validate=lambda x=fld.text:self.show_sugest(x))
        self.ids.mapa_layout.add_widget(fld)

    def define_ubi(self,id):
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
        self.ids.mapa.add_marker(MapMarkerPopup(lat=lat,lon=lng,source='Assets\images\map_marker.png'))


    def show_sugest(self,data):
        data=self.get_ubi(data)
        for i in data:
            id_value = i[1]  # Guarda el valor de 'data' en una variable
            self.ids.datos.add_widget(OneLineListItem(
                text=i[0],
                on_release=lambda _, id=id_value: self.define_ubi(id)
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
