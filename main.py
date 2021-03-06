import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date
import json
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)

dfCoor = json.load(open(r"C:\Users\Usuario\Desktop\PythonDataAnalisis\Proyecto\Cantones_de_Costa_Rica.geojson", "r"))
dataActive = pd.read_csv(r'C:\Users\Usuario\Desktop\PythonDataAnalisis\Proyecto\ACTIVOS.csv', delimiter=';',
                         encoding='latin-1')

dataActive["canton"] = dataActive["canton"].str.upper()
dataActive["Total"] = dataActive.iloc[:, -1]
dda = dataActive.groupby(['provincia']).sum()

total_prov = 0


def updateDict(x):
    global total_prov
    total_prov = {
        'San Jose': dda.loc['San Jose', x],
        'Alajuela': dda.loc['Alajuela', x],
        'Heredia': dda.loc['Heredia', x],
        'Cartago': dda.loc['Cartago', x],
        'Guanacaste': dda.loc['Guanacaste', x],
        'Puntarenas': dda.loc['Puntarenas', x],
        'Limon': dda.loc['Limon', x]
    }


# App layout
app.layout = html.Div([
    html.H1("Active Covid 19 cases Costa Rica", style={'text-align': 'center'}),
    dcc.Dropdown(id="select_provincia",
                 options=[
                     {"label": "San Jose", "value": "San Jose"},
                     {"label": "Alajuela", "value": "Alajuela"},
                     {"label": "Heredia", "value": "Heredia"},
                     {"label": "Cartago", "value": "Cartago"},
                     {"label": "Guanacaste", "value": "Guanacaste"},
                     {"label": "Puntarenas", "value": "Puntarenas"},
                     {"label": "Limon", "value": "Limon"},
                     {"label": "General CR", "value": "Todos"}],
                 multi=False,
                 value="Todos",
                 placeholder="Provincia",
                 style={'width': "40%"}
                 ),
    html.Br(),
    html.Div(id='output_container', children=[]),
    html.Div(id='output_container2', children=[]),
    html.Br(),
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=date(2020, 4, 21),
        max_date_allowed=date(2021, 7, 30),
        initial_visible_month=date(2020, 4, 21),
        date=date(2021, 7, 30)
    ),
    html.Br(),
    dcc.Graph(id='cr_map', figure={})
])


@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='output_container2', component_property='children'),
     Output(component_id='cr_map', component_property='figure')],
    [Input(component_id='select_provincia', component_property='value'),
     Input('my-date-picker-single', 'date')
     ]
)
def update_graph(option_slctd, date):
    updateDict(formatDate(date))
    container = "Costa rica"
    container2 = 'Total de casos: {}'.format(sum(total_prov.values()))

    dff = dataActive.copy()

    dffDates = dff.loc[:, [formatDate(date)]]
    dffDates["Total"] = dffDates.iloc[:, -1]
    dffHeader = dff.loc[:, :'canton']
    dff = pd.concat([dffHeader, dffDates], axis=1)

    """
    print(dffHeader)
    print(dffDates)
    print(dff)
    """

    if option_slctd != "Todos":
        dff = dff[dff["provincia"] == option_slctd]
        container = "Provincia: {}".format(option_slctd)
        container2 = "Total de casos: {}".format(total_prov[option_slctd])

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        geojson=dfCoor,
        locations=dff['canton'],  # nombre de la columna del Dataframe
        featureidkey='properties.NOM_CANT_1',
        # ruta al campo del archivo GeoJSON con el que se har?? la relaci??n (nombre de los estados)
        color="Total",  # El color depende de las cantidades
        color_continuous_scale="geyser"
    )

    fig.update_geos(showcountries=False, showcoastlines=True, showland=False, fitbounds="locations")
    return container, container2, fig  # add breakpoint


def formatDate(dates):
    aux = dates.split('-')
    return aux[2] + '/' + aux[1] + '/' + aux[0]


if __name__ == '__main__':
    app.run_server(debug=False)

""" Esto funciona AK7_________________
fig = px.choropleth(
                    data_frame=dataActive, 
                    geojson=dfCoor, 
                    locations=dataActive['canton'], # nombre de la columna del Dataframe
                    featureidkey='properties.NOM_CANT_1',  # ruta al campo del archivo GeoJSON con el que se har?? la relaci??n (nombre de los estados)
                    color= "Total", #El color depende de las cantidades
                    color_continuous_scale="geyser",
                      )
fig.update_geos(showcountries=False, showcoastlines=False, showland=False, fitbounds="locations")
fig.show()
"""
