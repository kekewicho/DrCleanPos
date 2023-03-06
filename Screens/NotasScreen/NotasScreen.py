from utils import (
    MDIconButton,
    MDDatePicker,
    Screen,
    MDDataTable,
    date,
    datetime,
    bd,
    dp,
    mainthread,
    pd,
    Thread
)

class BotonesNotas(MDIconButton):
    pass

class NotasScreen(Screen):
    #Construccion inicial de la pantalla
    def get_sub(self,artix):
        subtotal=0
        for i in artix:
            subtotal+=i.get('cantidad')*i.get('precio')
        return subtotal
    
    def df_to_datatable(self,dataframe):
        row_data = dataframe.to_records(index=False)
        return row_data
    
    def on_check_press(self, instance_table, current_row):
        self.check()
    
    @mainthread
    def create_dataTable(self,row_data):
        self.dataTable=MDDataTable(
                elevation=2,
                use_pagination=True,
                row_data=row_data,
                check=True,
                column_data=[
                    ("Cliente", dp(60)),
                    ("Fecha", dp(30)),
                    ("¿A domicilio?", dp(30)),
                    ("Total", dp(30)),
                    ("Saldo", dp(30)),
                    ("ID de nota", dp(60)),
                    ],
                )
        self.dataTable.bind(on_check_press=self.on_check_press)
        self.children[0].add_widget(self.dataTable)


    def load_data(self):
        data=bd.child('notas').get()
        self.notas=pd.DataFrame(data.val(),index=None).transpose()
        self.notas=self.notas.reset_index(drop=False)
        self.notas['subtotal']=self.notas['articulos'].apply(self.get_sub)
        self.notas['total']=self.notas['subtotal']+self.notas['envio']-self.notas['descuentos']
        self.notas['saldo']=self.notas['total']-self.notas['abonos']
        Thread(self.manager.get_screen('Reportes_Screen').render_plot_ventasmes(self.notas)).start()
        data_ventas=self.notas[['usuario_name','fecha','a domicilio','total','saldo','usuario']]
        data_ventas['total']=data_ventas['total'].apply(lambda x:'${:,.2f}'.format(x))
        data_ventas['a domicilio']=data_ventas['a domicilio'].apply(lambda x: 'SI' if x else 'NO')
        data_ventas['saldo']=data_ventas['saldo'].apply(lambda x:('cash-clock',[248/256,236/256,14/256,1],'${:,.2f}'.format(x)) if x>0 else ('cash-check',[29/256,143/256,12/256,1],'${:,.2f}'.format(x)))
        data_ventas.sort_values(by='fecha',inplace=True,ascending=False)
        row_data = self.df_to_datatable(data_ventas)
        self.create_dataTable(row_data)
        print(self.notas.columns)


    #Codigo y funciones del funcionamiento de la pantalla de Notas
    date_dialog=None
    def check(self):
        if len(self.children[0].children[0].get_row_checks())==0:
            self.ids.layout_btns.clear_widgets()
            return None
        if len(self.children[0].children[0].get_row_checks())>1:
            botones=('printer','file-image-outline','delete')
        if len(self.children[0].children[0].get_row_checks())==1:
            botones=('open-in-new','printer','file-image-outline','delete')
        self.ids.layout_btns.clear_widgets()
        for i in botones: self.ids.layout_btns.add_widget(BotonesNotas(icon=i,theme_icon_color= "Custom",icon_color= '#ffffff',rounded_button=False))

    def eliminar(self):
        pass

    def printTicket(self):
        pass

    def eticket(self):
        pass

    def open_nota(self):
        notaid=self.children[0].children[0].get_row_checks()[0][-1]

        self.manager.current='Venta_Screen'
        nota=(bd.child('notas').order_by_key().equal_to(notaid).get())[0]
        scr=self.manager.get_screen('Venta_Screen')
        scr.clean()

        #Definiendo el usuario
        scr.define_user(nota.val()['usuario_name'],nota.val()['usuario'],notaid)
        
        #Agregando servicios
        sub=0
        for service in nota.val()['articulos']:
            if service['servicio']!='ROPA PARA LAV/KG':cant=int(service['cantidad'])
            else:cant=service['cantidad']
            scr.add_service(service['servicio'],cant)
        
        if nota.val()['a domicilio']:scr.ids.check_envio.active==True
        scr.ids.descuento.text='${:,.2f}'.format(nota.val()['descuentos'])
        scr.ids.abono.text='${:,.2f}'.format(nota.val()['abonos'])
        scr.update_sub()

        #Actualizando fecha como variable global
        scr.get_date('instance',nota.val()['fecha'],'date_range')

        #Cambiando el valor seleccionado del menuBar izquierdo
        scr.manager.parent.children[-1].ids.box_items.children[-1].active=True
        scr.manager.parent.children[-1].ids.box_items.children[-2].active=False
        
    def search(self,value:str,fecha_inicio:str,fecha_final:str):
        fi=fecha_inicio if fecha_inicio!='' else '2000-1-1'
        ff=fecha_final if fecha_final!='' else str(date.today())
        data_ventas=self.notas[['index','usuario_name','fecha','a domicilio','total','saldo','usuario']]
        data_ventas['fecha']=pd.to_datetime(data_ventas['fecha'],format='%Y-%m-%d')
        data_ventas=data_ventas[((data_ventas['index']==value) | (data_ventas['usuario_name'].str.upper().str.contains(value.upper())) | (data_ventas['usuario']==value)) & ((data_ventas['fecha']>=fi) & (data_ventas['fecha']<=ff))]
        data_ventas.drop('index', axis=1, inplace=True)
        data_ventas['fecha']=data_ventas['fecha'].dt.date
        data_ventas['total']=data_ventas['total'].apply(lambda x:'${:,.2f}'.format(x))
        data_ventas['a domicilio']=data_ventas['a domicilio'].apply(lambda x: 'SI' if x else 'NO')
        data_ventas['saldo']=data_ventas['saldo'].apply(lambda x:('cash-clock',[248/256,236/256,14/256,1],'${:,.2f}'.format(x)) if x>0 else ('cash-check',[29/256,143/256,12/256,1],'${:,.2f}'.format(x)))
        data_ventas.sort_values(by='fecha',inplace=True,ascending=False)
        row_data = self.df_to_datatable(data_ventas)
        self.dataTable.row_data=row_data

    def on_save_ff(self, instance, value, date_range):
        self.ids.ff.text=str(value)
    
    def on_save_fi(self, instance, value, date_range):
        self.ids.fi.text=str(value)

    def on_cancel(self, instance, value):
        pass

    def show_date_picker(self,field):
        self.date_dialog = MDDatePicker()
        self.date_dialog.bind(on_save=self.on_save_ff if field=='ff' else self.on_save_fi, on_cancel=self.on_cancel)
        self.date_dialog.open()
