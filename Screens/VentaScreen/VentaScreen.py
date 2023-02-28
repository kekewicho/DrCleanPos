from Widgets.widgets import BtnServicio
from kivymd.uix.screen import Screen
from kivy.clock import mainthread
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton,MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList
from kivymd.uix.card import MDCardSwipe,MDCard
from kivy.animation import Animation
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDDatePicker
from datetime import date
import database

#Variables globales
selected_client=''
fecha=date.today()
idActual=None

class ButtonClean(MDCard):
    pass

class UserItem(MDCard):
    pass

class ServiceItem(MDCardSwipe):
    pass

class ContentUser(MDBoxLayout):
    pass

class VentaScreen(Screen):
    dialog=None

    #Ejecución inicial de la app
    def load_services(self):
        servicios=database.bd.child('servicios').get()
        for i in servicios.each():
            for j in i.val():
                self.build_ui(j)
                database.lista_precios[j]=i.val()[j]

    @mainthread
    def build_ui(self,txt):
        cont=BtnServicio()
        cont.ids.srvc.text= txt.replace('-',' / ')
        self.ids.servicios.add_widget(cont)

    #Funciones de la pantalla
    def set_envio(self,state):
        if state:
            amount=float((self.ids.subtotal.text).replace('$','').replace(',',''))-float((self.ids.descuento.text).replace('$','').replace(',',''))
            if amount<200: self.ids.envio.text='${:,.2f}'.format(70)
            if amount>=200 and amount<300:self.ids.envio.text='${:,.2f}'.format(50)
            if amount>=300:self.ids.envio.text='${:,.2f}'.format(0)
        else:
            self.ids.envio.text='${:,.2f}'.format(0)

    def guardar(self,something):
        global selected_client
        data={}
        for i in self.dialog.content_cls.children:
            if 'Nombre' in i.hint_text:data['nombre']=i.text
            if 'Apellido' in i.hint_text:data['apellido']=i.text
            if 'Teléfono' in i.hint_text:data['telefono']=i.text
            if 'Domicilio' in i.hint_text:data['domicilio']=i.text
        new_user=database.bd.child('clientes').push(data)
        userid=new_user['name']
        selected_client=userid
        print(selected_client)
        self.define_user(data.get('nombre')+' '+data.get('apellido'),userid)
        self.dialog.dismiss()
    
    def switch_newselect(self,something=None):
        self.dialog.dismiss()
        content=ContentUser()
        content.clear_widgets()
        for i in (['Nombre(s)','account'],['Apellido(s)','account'],['Domicilio','map-marker'],['Teléfono','phone-classic']):
            fld=MDTextField(icon_left=i[1],hint_text=i[0],write_tab= False)
            content.add_widget(fld)
        self.dialog = MDDialog(
            title="Agregar nuevo usuario",
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    on_release=self.cancel
                ),
                MDFlatButton(
                    text="GUARDAR",
                    theme_text_color="Custom",
                    on_release=self.guardar
                )
            ],
        )
        self.dialog.open()
        anim=Animation(height=280,duration=1,transition='out_elastic')
        anim.start(content.parent)

    def define_user(self,nombre,userid,idnota=None):
        global selected_client,idActual
        idActual=idnota
        selected_client=userid
        if self.dialog:self.dialog.dismiss()
        self.ids.user.text=nombre
        self.ids.user.text_color="#ffffff"
        self.ids.user_icon.text_color='#ffffff'
        self.ids.user_icon.icon='account-check'
        self.ids.user_card.md_bg_color='#089cba'
        if len(self.ids.user_area.children)==1:self.ids.user_area.add_widget(ButtonClean())

    def search(self):        
        if len(self.dialog.content_cls.ids.barra_busqueda.children)<2:
            self.dialog.content_cls.ids.barra_busqueda.add_widget(MDIconButton(
                icon='plus-circle',
                on_release=self.switch_newselect)
            )
        cliente=self.dialog.content_cls.ids.cliente.text
        self.dialog.content_cls.ids.lista_usuarios.clear_widgets()
        lista=MDList()
        for i in database.clientes:
            if cliente.upper() in str(database.clientes[i]['nombre']).upper() or cliente.upper() in str(database.clientes[i]['apellido']).upper():
                item=UserItem()
                item.ids.nombre.text=str(database.clientes[i].get('nombre'))+' '+str(database.clientes[i].get('apellido'))
                item.ids.domicilio.text='Domicilio: '+str(database.clientes[i].get('domicilio'))
                item.ids.telefono.text='Teléfono: '+str(database.clientes[i].get('telefono'))
                item.ids.userid.text=str(i)
                lista.add_widget(item)
        self.dialog.content_cls.ids.lista_usuarios.add_widget(lista)

    def update_sub(self):
        sub=0
        for i in self.ids.articulos_nota.children:
            precio=eval((i.ids.precio.text).replace('$',''))
            cantidad=eval(i.ids.cantidad.text)
            sub+=precio*cantidad
        self.ids.subtotal.text="${:,.2f}".format(sub)
        total=0
        if self.ids.check_descuento.active:self.ids.descuento.text='${:,.2f}'.format(self.descuento())
        if self.ids.check_envio.active:self.ids.envio.text='${:,.2f}'.format(self.envio())
        for j in self.ids.desgloses.children:
            if j.children[-1].text=='Descuentos:':total-=eval((self.ids.descuento.text).replace('$','').replace(',',''))
            elif j.children[-1].text=='Saldo:':pass
            elif j.children[-1].text=='Envío:':total+=eval((self.ids.envio.text).replace('$','').replace(',',''))
            elif j.children[-1].text=='Abonos:':total-=eval((self.ids.abono.text).replace('$','').replace(',',''))
            else:total+=eval((j.children[0].text).replace('$','').replace(',',''))
        self.ids.saldo.text="${:,.2f}".format(total)
        if len(self.ids.user_area.children)==1:self.ids.user_area.add_widget(ButtonClean())


    def add_service(self,service,cant=1):
        if service=='ROPA PARA LAV/KG':
            item=ServiceItem()
            item.ids.cantidad.text='{:,.1f}'.format(cant)
            item.ids.servicio.text=service
            item.ids.precio.text="${:,.2f}".format(database.lista_precios.get(service.replace('/','-')))
            self.ids.articulos_nota.add_widget(item,len(self.ids.articulos_nota.children))
            self.update_sub()
            return None

        for i in self.ids.articulos_nota.children:
            if i.ids.servicio.text==service:
                i.ids.cantidad.text=str(eval(i.ids.cantidad.text)+1)
                self.update_sub()
                return None
        item=ServiceItem()
        item.ids.cantidad.text=str(cant)
        item.ids.servicio.text=service
        item.ids.precio.text="${:,.2f}".format(database.lista_precios.get(service.replace(' / ','-')))
        self.ids.articulos_nota.add_widget(item,len(self.ids.articulos_nota.children))
        self.update_sub()

    def selector(self,pos):
        anim=Animation(size_hint=(0,0),duration=.1)+Animation(pos_hint={'center_x':pos},duration=.05)+Animation(size_hint=(.30,.8),duration=.2)
        anim.start(self.ids.selector)

    def cancel(self,something):
        self.dialog.dismiss()

    def user_define(self):
        content=ContentUser()
        users=database.bd.child('clientes').get()
        for i in users.each():
            database.clientes[i.key()]=i.val()
        self.dialog = MDDialog(
            title="Selecciona un cliente",
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    on_release=self.cancel
                )
            ],
        )
        self.dialog.open()
    
    def descuento(self):
        menor={}
        cant_descuentos=0
        servicios={}
        for i in self.ids.articulos_nota.children:
            if 'EDRE' in i.ids.servicio.text or 'COBER' in i.ids.servicio.text or 'COLCHA' in i.ids.servicio.text or 'COBIJA' in i.ids.servicio.text:
                servicios[i.ids.servicio.text]={'cantidad':int(i.ids.cantidad.text),'precio':float((i.ids.precio.text).replace('$','').replace(',',''))}
                menor[i.ids.servicio.text]=float((i.ids.precio.text).replace('$','').replace(',',''))
                cant_descuentos+=int(i.ids.cantidad.text)
        cant_descuentos=int(cant_descuentos/3)
        if cant_descuentos==0: return 0
        i=0
        menor=sorted(menor.items(), key=lambda x:x[1])
        monto_descontado=0
        while True:
            if (servicios.get(menor[0][0]).get('cantidad'))*2>=cant_descuentos:
                monto_descontado+=servicios.get(menor[i][0]).get('precio')*.5*cant_descuentos
                break
            else:
                monto_descontado+=servicios.get(menor[0][0]).get('precio')*servicios.get(menor[i][0]).get('cantidad')
                cant_descuentos-=servicios.get(menor[0][0]).get('cantidad')*2
                menor.pop(0)
        return monto_descontado
    
    def envio(self):
        subtotal=float((self.ids.subtotal.text).replace('$','').replace(',',''))
        descuento=float((self.ids.descuento.text).replace('$','').replace(',',''))
        if subtotal-descuento<200:return 70
        if subtotal-descuento>=200 and subtotal-descuento<300:return 50
        if subtotal-descuento>=300:return 0

    def venta(self,abono=0):
        global selected_client,fecha,idActual
        
        if selected_client=='':
            MDSnackbar(MDLabel(text='No has selecionado ningun usuario',theme_text_color="Custom",
            text_color="#ffffff",)).open()
            return None
        if len(self.ids.articulos_nota.children)==0:
            MDSnackbar(MDLabel(text='La nota no contiene ningún artículo',theme_text_color="Custom",
            text_color="#ffffff",)).open()
            return None
       
        if abono==-1:
            total=float((self.ids.subtotal.text).replace('$','').replace(',',''))+float((self.ids.envio.text).replace('$','').replace(',',''))-float((self.ids.descuento.text).replace('$','').replace(',',''))
            self.ids.abono.text='${:,.2f}'.format(total)
        else:
            self.ids.abono.text='${:,.2f}'.format(float((self.ids.abono.text).replace('$','').replace(',',''))+abono)

        data={}
        data['usuario']=selected_client
        data['usuario_name']=self.ids.user.text
        data['a domicilio']=True if self.ids.check_envio.active else False
        data['descuentos']=float((self.ids.descuento.text).replace('$','').replace(',',''))
        data['envio']=float((self.ids.envio.text).replace('$','').replace(',',''))
        data['abonos']=float((self.ids.abono.text).replace('$','').replace(',',''))
        data['fecha']=str(fecha)
        articulos=[]
        for i in self.ids.articulos_nota.children:
            item={}
            item['servicio']=i.ids.servicio.text
            item['cantidad']=float('{:.2f}'.format(float(i.ids.cantidad.text)))
            item['precio']=float((i.ids.precio.text).replace('$','').replace(',',''))
            articulos.append(item)
        data['articulos']=articulos
        if idActual==None:
            database.bd.child('notas').push(data)
            MDSnackbar(MDLabel(text='Venta realizada con éxito',theme_text_color="Custom",
                text_color="#ffffff",)).open()
        if idActual!=None:
            database.bd.child(f'notas/{idActual}').update(data)
            MDSnackbar(MDLabel(text='Nota actualizada con éxito',theme_text_color="Custom",
                text_color="#ffffff",)).open()

        self.clean()
    
    def abono(self):
        def cancelar(object):
            dialog.dismiss()
            MDSnackbar(MDLabel(text='Operación cancelada',theme_text_color="Custom",
            text_color="#ffffff")).open()

        def guardar(comething):
            self.venta(float(dialog.content_cls.children[0].text))
            dialog.dismiss()
        
        content=MDBoxLayout(size_hint_y=None,height='50dp')
        content.add_widget(MDTextField(hint_text='Cantidad a abonar',on_text_validate=guardar))

        dialog=MDDialog(
            title='Ingresar abono',
            content_cls=content,
            type='custom',
            buttons=[
                MDFlatButton(
                    text='CANCELAR',
                    on_release=cancelar
                ),
                MDFlatButton(
                    text='GUARDAR',
                    on_release=guardar
                )
            ]
        )
        dialog.open()
    
    def get_date(self,instance,value,date_range):
        global fecha
        if value==date.today():return None
        fecha=value
        self.ids.date_selector.md_bg_color='#089cba'
        self.ids.date_selector_icon.text_color='#ffffff'
        if len(self.ids.user_area.children)==1:self.ids.user_area.add_widget(ButtonClean())
    
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.get_date,on_cancel=self.on_cancel)
        date_dialog.open()

    def on_cancel(self,instance,value):
        pass

    def get_cant(self):
        def guardar(something):
            self.add_service('ROPA PARA LAV/KG',float(self.dialog.content_cls.text))
            self.dialog.dismiss()

        self.dialog=MDDialog(
            title='Introduce peso',
            type='custom',
            content_cls=MDTextField(hint_text='Peso en kg',on_text_validate=guardar),
            buttons=[
                MDFlatButton(
                    text='CANCELAR',
                    on_release=self.cancel
                ),
                MDFlatButton(
                    text='GUARDAR',
                    on_release=guardar)

            ]
        )
        self.dialog.open()

    def clean(self):
        global selected_client, fecha,idActual
        idActual=None
        self.ids.user_card.md_bg_color='#dadada'
        self.ids.user_icon.text_color= "#8d8d8d"
        self.ids.user_icon.icon='account'
        self.ids.user.text='Click para seleccionar usuario'
        self.ids.user.text_color= "#8d8d8d"
        self.ids.check_envio.active=False
        self.ids.check_descuento.active=True
        self.ids.articulos_nota.clear_widgets()
        fecha=date.today()
        self.ids.date_selector.md_bg_color='#dadada'
        self.ids.date_selector_icon.text_color='#8d8d8d'
        selected_client=''
        self.selector(1/6)
        for i in self.ids.selector.parent.children[0].children:i.children[0].active=False
        self.ids.s_abono.active=True
        for i in ('subtotal','envio','descuento','abono','saldo'):
            self.ids[i].text='${:,.2f}'.format(0)
        if len(self.ids.user_area.children)>1:self.ids.user_area.remove_widget(self.ids.user_area.children[0])
        
