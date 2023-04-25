from utils import (
    Screen,
    Animation,
    bd,
    MDSnackbar,
    MDFlatButton,
    MDLabel,
    pd,
    ak
)

from Widgets.widgets import ActivosCard

class ActivosScreen(Screen):
    servicios=[]
    def set_cards(self,data):
        for key,value in data.iterrows():
            value['fecha']=value['fecha'].strftime('%Y-%m-%d %H:%M')
            self.add_card(value)

    def selector(self,pos,selected):
        anim=Animation(size_hint=(0,0),duration=.1)+Animation(pos_hint={'center_x':pos},duration=.05)+Animation(size_hint=(.185,.8),duration=.2)
        anim.start(self.ids.selector)
        target=self.setSelector(selected)

    def add_card(self,data):
        async def add_card():
            card=ActivosCard(
                idNota=data['index'],
                userName=data['usuario_name'],
                status=data['status'],
                fecha=data['fecha'],
                aDomicilio=data['a domicilio'],
                total=data.get('total'),
                saldo=data.get('saldo')
                )
            card.ids.statusIcon.on_release=lambda x=card:self.updateStatus(x)
            self.ids.activos_layout.add_widget(card)
            self.servicios.append(card)
        ak.start(add_card())
    
    def updateStatus(self,card:ActivosCard):
        status=card.status
        if status=='recoleccion':new_status='sucursal'
        if status=='sucursal':new_status='entrega'
        if status=='entrega':new_status='finalizado'
        bd.child(f'notas/{card.id_nota}').child('status').set(new_status)
        if new_status=='finalizado':
            self.ids.activos_layout.remove_widget(card)
            self.servicios.remove(card)
            MDSnackbar(MDLabel(text='El servicio ha sido marcado como entregado'),MDFlatButton(text='DESHACER',on_release=lambda x=card,old=status:x.setStatus(old))).open()
            return None
        card.setStatus(new_status)
        MDSnackbar(MDLabel(text='Estatus de servicio actualizado'),MDFlatButton(text='DESHACER',on_release=lambda x=card,old=status:x.setStatus(old))).open()

    def setSelector(self,selected):
        async def setSelector():
            self.ids.activos_layout.clear_widgets()
            if selected=='Todo':
                for i in self.servicios:self.ids.activos_layout.add_widget(i)
            if selected in ['entrega','sucursal','recoleccion']:
                for i in self.servicios:
                    if i.status==selected:self.ids.activos_layout.add_widget(i)
            if selected=='Rezagado':
                for i in self.servicios:
                    if (pd.Timestamp.now()-pd.to_datetime(i.fecha)).days>=14:
                        self.ids.activos_layout.add_widget(i)
        ak.start(setSelector())
    
    def eventListener(self,message):
        async def eventListener():
            if message['event']=='patch':
                data={}
                for key,value in message['data'].items():
                    data=value
                    data['index']=key
                self.add_card(data)
        ak.start(eventListener())
