from utils import (
    Screen,
    FigureCanvasKivyAgg,
    pd,
    bd,
    plt,
    ticker,
    mainthread
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

    @mainthread
    def render_plot_ventasmes(self,ventas):
        df=ventas[['fecha','total']]
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['mes'] = df['fecha'].dt.month
        df['mes']=df['mes'].apply(self.get_month_name)
        ventas_por_mes = df.groupby('mes').sum()

        # Imprime las ventas por mes
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
