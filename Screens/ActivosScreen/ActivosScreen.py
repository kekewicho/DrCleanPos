from utils import (
    Screen,
    Animation,
    mainthread,
    bd,
    MDSnackbar,
    MDFlatButton,
    MDLabel,
    Thread,
    date,
    pd
)

from Widgets.widgets import ActivosCard

class ActivosScreen(Screen):
    servicios=[]
    def set_cards(self,data:pd.Dataframe()):
        for key,value in data.iterrows():
            self.add_card(value)

    def selector(self,pos,selected):
        anim=Animation(size_hint=(0,0),duration=.1)+Animation(pos_hint={'center_x':pos},duration=.05)+Animation(size_hint=(.185,.8),duration=.2)
        anim.start(self.ids.selector)
        Thread(target=self.setSelector(selected)).start()

    @mainthread
    def add_card(self,data):
        card=ActivosCard(
            idNota=data['index'],
            userName=data['usuario_name'],
            status=data['status'],
            fecha=data['fecha'],
            aDomicilio=data['a domicilio'],
            total=data['total'],
            saldo=data['saldo']
            )
        card.ids.statusIcon.on_release=lambda x=card:self.updateStatus(x)
        self.ids.activos_layout.add_widget(card)
        self.servicios.append(card)
    
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

    @mainthread
    def setSelector(self,selected):
        self.ids.activos_layout.clear_widgets()
        if selected=='Todo':
            for i in self.servicios:self.ids.activos_layout.add_widget(i)
        if selected in ['entrega','sucursal','recoleccion']:
            for i in self.servicios:
                if i.status==selected:self.ids.activos_layout.add_widget(i)
        if selected=='Rezagado':
            for i in self.servicios:
                if (pd.Timestamp.now().strftime('%Y-%m-%d')-pd.to_datetime(i.fecha)).days>=14:
                    self.ids.activos_layout.add_widget(i)
