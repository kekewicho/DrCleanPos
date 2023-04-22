from utils import (
    Screen,
    FigureCanvasKivyAgg,
    pd,
    bd,
    plt,
    ticker,
    ak
)


class ReportesScreen(Screen):
    def get_month_name(self,month):
        meses={
            1:'Enero',
            2:'Febrero',
            3:'Marzo',
            4:'Abril',
            5:'Mayo',
            6:'Junio',
            7:'Julio',
            8:'Agosto',
            9:'Septiembre',
            10:'Octubre',
            11:'Noviembre',
            12:'Diciembre'
        }
        return meses.get(month)

    def render_plot_ventasmes(self,ventas:pd.DataFrame):
        async def render_plot_ventasmes():
            df=ventas
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['mesnumero'] = df['fecha'].dt.month
            df['mes']=df['mesnumero'].apply(self.get_month_name)
            df=df[df['fecha'].dt.year==pd.Timestamp.now().year]
            df=df[['mesnumero','total']]
            ventas_por_mes = df.groupby('mesnumero').sum()
            ventas_por_mes = ventas_por_mes.sort_values('mesnumero')
            print(ventas_por_mes)

            # Crea el gráfico
            fig, ax = plt.subplots()

            # Reemplaza los valores de x_new y y_new con las fechas y las ventas por mes
            x_new = ventas_por_mes.index
            y_new = ventas_por_mes['total']

            ax.fill_between(x_new, y_new, 0, color='#2698c4', alpha=0.2)
            plt.xticks(x_new)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
            for y in range(0, int(max(y_new)) + 500, 5000):
                plt.axhline(y, color='lightgray', alpha=0.3, linestyle='dotted')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            
            self.ids.graph_ventas.add_widget(canvas)
            
            kpis_data=df['total'][df['mesnumero']==pd.Timestamp.now().month]
            kpis_data_ant=df['total'][df['mesnumero']==pd.Timestamp.now().month-1]
            if kpis_data.shape[0]==0: return None
            #KPI monto
            self.ids.kpis_monto.text='${:,.2f}'.format(kpis_data.sum())
            dif=float((kpis_data.sum()-kpis_data_ant.sum())/kpis_data.sum())*100
            self.ids.kpis_monto_comparacion.text=f"{'{:.1f}%'.format(dif)} que el mes anterior"

            #KPI cantidad
            self.ids.kpis_cantidad.text=str(kpis_data.shape[0])
            dif=float((kpis_data.shape[0]-kpis_data_ant.shape[0])/kpis_data.shape[0])*100
            self.ids.kpis_cantidad_comparacion.text=f"{'{:.1f}%'.format(dif)} que el mes anterior"
            
            #KPI ticket promedio
            self.ids.kpis_monto.text='${:,.2f}'.format(kpis_data.mean())
            dif=float((kpis_data.mean()-kpis_data_ant.mean())/kpis_data.mean())*100
            self.ids.kpis_monto_comparacion.text=f"{'{:.1f}%'.format(dif)} que el mes anterior"
        ak.start(render_plot_ventasmes())