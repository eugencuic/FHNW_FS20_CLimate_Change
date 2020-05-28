import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
from dash.dependencies import Input, Output
import pandas as pd
import sqlalchemy
import get_city_weather
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import os

#Code für den Server

# Create the data for connecting to the database
database_username = 'climate_change'
database_password = 'FHNW_climate_20'
database_ip = '45.32.156.57'
database_name = 'Climate_Change'

# The connection to the database will be made, in the callback functions
database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                               format(database_username, database_password,
                                                      database_ip, database_name))

# Evoke Connection
con = database_connection.connect()

# Select the needed columns and put them in a pandas dataframe
select_coordinates = pd.read_sql('SELECT Ortschaftsname, Longitude, Latitude FROM coordinates', con=con)

# Close the database connection
con.close()

# Create a dash object and add a sylesheet for making the layout of the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the Layout of the app
app.layout = dbc.Container(
    [html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    'Falls ein Fehler auftaucht laden Sie die Webseite bitte neu'
                                ),
                                style={
                                    'font-size': 28,
                                    'color': 'red',
                                }
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                html.H1(
                                    'Webseite des Projektes Climate Change des Studiengangs Data Science der FHNW',
                                    style={
                                        'textAlign': 'center',
                                        'margin': 20
                                    }
                                )
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown('''
                                    Auf dieser Webseite finden Sie Grafiken, welche den Klimawandel visualisieren und auf welcher Sie 
                                    Informationen über das Klima in der Schweiz finden können.  

                                    Die Visualisierungen die Sie hier finden, sind ergänzend zu einer Story über das Klima und den Wein. Die 
                                    Story finden Sie mit folgendem Link: [Warum ein warmer Sommer zu einem tränenreichen Herbst führt](https://medium.com/@lukasreber/warum-ein-warmer-sommer-zu-einem-tr%C3%A4nenreichen-herbst-f%C3%BChrt-f74960db12ae)

                                    Kurz zusammenfassend führen höhere Temperaturen zu einem höheren Zuckergehalt in den Weintrauben. 
                                    Ein höherer Zuckergehalt wiederum, führt zu einem höheren Alkoholgehalt später im Wein.  

                                    Wie Sie aus den nachfolgenden Grafiken entnehmen können, wird das Klima wärmer, was zu einem höheren Alkoholgehalt in unseren 
                                    Weinen führen kann. (Für Details zum Wein verweisen wir Sie wieder auf obigen Link, wo das genau erklärt ist).  

                                    Im folgenden können Sie sich die Grafiken ansehen und sich selber eine Meinung über das Klima in der Schweiz bilden.
                                    ''',
                                             style={
                                                 'margin': 30
                                             }
                                             )
                            )
                        ]
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                'Gesamtübersicht des Wetters in der Schweiz'
                            )
                        ]
                    )
                ],
                style={
                    'margin': 40
                }
            ),
            dbc.Row(
                [
                    dbc.Col([
                        # Dropdown for selecting the temperatur or Precicipation
                        html.Div(
                            dcc.Dropdown(
                                id='weather-dropdown',
                                options=[{'label': 'Niederschlag', 'value': 'Niederschlag'},
                                         {'label': 'Temperatur', 'value': 'Temperatur'}
                                         ],
                                value='Niederschlag',
                                clearable=False
                            )
                        )
                    ], width=8
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    '**BEDIENHINWEIS:** Wählen Sie aus, ob Sie die Temperatur- oder Niederschlagsentwicklung in der Schweiz betrachten möchten.',
                                    style={
                                        'font-size': 12
                                    }
                                )
                            )
                        ]
                    ),
                ],
                style={
                    'margin': 30
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            # Slider for selecting the year
                            html.Div(
                                dcc.Slider(
                                    id='year-slider',
                                    min=1961,
                                    max=2019,
                                    value=1961,
                                    step=1,
                                    marks={'1961': '1961',
                                           '1970': '1970',
                                           '1980': '1980',
                                           '1990': '1990',
                                           '2000': '2000',
                                           '2010': '2010',
                                           '2019': '2019'
                                           },
                                    updatemode='drag'
                                )
                            )
                        ], width=10
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    '**BEDIENHINWEIS:** Wählen Sie das gewünschte Jahr aus.',
                                    style={
                                        'font-size': 12
                                    }
                                )
                            )
                        ]
                    ),
                ],
                style={
                    'margin': 30
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            # Slider for selecting the month
                            html.Div(
                                dcc.Slider(
                                    id='month-slider',
                                    min=1,
                                    max=12,
                                    value=1,
                                    step=1,
                                    marks={'1': 'Jan',
                                           '2': 'Feb',
                                           '3': 'März',
                                           '4': 'Apr',
                                           '5': 'Mai',
                                           '6': 'Juni',
                                           '7': 'Juli',
                                           '8': 'Aug',
                                           '9': 'Sep',
                                           '10': 'Okt',
                                           '11': 'Nov',
                                           '12': 'Dez'
                                           },
                                    updatemode=('drag')
                                )
                            )
                        ], width=10
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    '**BEDIENHINWEIS:** Wählen Sie den gewünschten Monat aus.',
                                    style={
                                        'font-size': 12
                                    }
                                )
                            )
                        ]
                    ),
                ],
                style={
                    'margin': 20
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                # HTML Tag where the image will show up
                                html.Img(
                                    id='show_image',
                                    style={
                                        'textAlign': 'center'
                                    }
                                )
                            )
                        ]
                    )
                ],
                style={
                    'margin': 0
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown('''
                                **KARTENERKLÄRUNG**  
                                Auf der Karte obigen, finden Sie das ausgewählte Wetter (Temperatur oder Niederschlag) visualisiert über 
                                der ganzen Schweiz, für den Monat und das Jahr, welches Sie ausgewählt haben.  

                                Unter der Karte, finden Sie eine Skala, auf der Sie den Farben genaue Werte zuordnen können (z. B. dunkelrot=30°C, 
                                oder dunkelviolett=400 mm Regen pro Monat).
                        '''
                                             )
                            )
                        ]
                    ),
                ],
                style={
                    'margin': 0
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                'Wetterübersicht nach Ortschaft'
                            )
                        ]
                    )
                ],
                style={
                    'margin': 40
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Dropdown(
                                    id='cities-dropdown',
                                    placeholder='Wählen Sie eine Stadt',
                                    clearable=False
                                )
                            )
                        ], width=6
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    '**BEDIENHINWEIS:** Wählen Sie eine Ortschaft aus, für welche Sie den Temperatur- und Niederschlagsmengenverlauf der Jahre 1961 - 2019 wissen möchten. '
                                    'In den folgenden vier Plots, können sie mittels Anwählen eines bestimmten Ausschnitts der Grafik, diesen Ausschnitt vergrössern. '
                                    'Indem Sie bei der Legende eine Linie anwählen, wird nur diese Linie dargestellt (Grafiken 1 und 3).',
                                    style={
                                        'font-size': 12
                                    }
                                )
                            )
                        ]
                    ),
                ],
                style={
                    'margin': 40
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                html.H3(
                                    'Temperatur'
                                )
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Graph(
                                    id='Scatter_Temp'
                                )
                            )
                        ], width=9
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown('''
                                    **ERKLÄRUNG**  
                                    *Punkte:* Ein Punkt repräsentiert einen die Temperatur in einem Monat  

                                    *Gezackte Linie:* Diese Linie, zeigt immer die durchschnittliche Temperatur der letzten 12 Monate an
                                    ''',
                                             style={
                                                 'font-size': 14
                                             }
                                             )
                            )
                        ]
                    ),
                ],
                style={
                    'margin': 20
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Graph(
                                    id='Change_Temp'
                                )
                            )
                        ],
                        width=9
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown('''
                                                **ERKLÄRUNG**  
                                                Die Abweichung eines Balkens von der Nulllinie, zeigt die Abweichung der Temperatur 
                                                von der durchschnittlichen Temperatur in den Jahren 1961 - 2019 
                                                in diesem Jahr in dem der Balken steht an.
                                                ''',
                                             style={
                                                 'font-size': 14
                                             }
                                             )
                            )
                        ]
                    )
                ],
                style={
                    'margin': 10
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                html.H3(
                                    'Niederschlag'
                                )
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Graph(
                                    id='Scatter_Prec'
                                )
                            )
                        ],
                        width=9
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown('''
                                **ERKLÄRUNG**  
                                *Punkte:* Ein Punkt repräsentiert einen die Temperatur in einem Monat  

                                *Gezackte Linie:* Diese Linie, zeigt immer die durchschnittliche Temperatur der letzten 12 Monate an  
                                ''',
                                             style={
                                                 'font-size': 14
                                             }
                                             )
                            )
                        ]
                    )
                ],
                style={
                    'margin': 10
                }
            ), dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            dcc.Graph(
                                id='Change_Prec'
                            )
                        )
                    ],
                    width=9
                ),
                dbc.Col(
                    [
                        html.Div(
                            dcc.Markdown('''
                                    **ERKLÄRUNG**  
                                    Die Abweichung eines Balkens von der Nulllinie, zeigt die Abweichung der Niederschlagsmenge 
                                    von der durchschnittlichen Menge des Niederschlags in den Jahren 1961 - 2019 
                                    in diesem Jahr in dem der Balken steht an.
                                    ''',
                                         style={
                                             'font-size': 14
                                         }
                                         )
                        )
                    ]
                )
            ],
            style={
                'margin': 10
            }
        ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown('''
                                    **Quellenangaben:**  

                                    * Die Niederschlags- und Temperaturdaten stammen von [MeteoSchweiz](https://www.meteoschweiz.admin.ch/home.html?tab=overview).  
                                    * Die Namen aller Schweizer Städte stammen von der Webseite [Cadastre](https://www.cadastre.ch/de/services/service/registry/plz.html) der Schweizerischen Eidgenossenschaft.  

                                    **Mitwirkende**  

                                    * Christopher Frame, Lukas Reber, Eugen Cuic, Cédric Künzi                                    
                                    * Studenten Studiengang BSc Data Science der Fachhochschule Nordwestschweiz
                                    ''',
                                             style={
                                                 'font-size': 12
                                             }
                                             )
                            )
                        ]
                    ),
                ],
                style={
                    'margin': 30
                }
            ),
        ]
    )
    ]
)

# Define where the output goes and from where the input comes in
#For changing the map if the client wants to see another year or month
@app.callback(
    Output('show_image', 'src'),
    [Input('year-slider', 'value'),
     Input('month-slider', 'value'),
     Input('weather-dropdown', 'value')])

# Define what will be done if an input variable is changing
def update_figure(selected_year, selected_month, weather):
    image_path = os.path.join(os.path.expanduser('~'),'climate_change','Images','{}_{}_{}.png').format(weather,selected_year,selected_month)

    image_file = open(image_path, 'rb').read()
    encoded_image = (base64.b64encode(image_file))
    return 'data:image/png;base64,{}'.format(encoded_image.decode())


#Make a function, that returns a list in the dropdown with all the cities you can choose
@app.callback(
    Output('cities-dropdown', 'options'),
    [Input('cities-dropdown', 'value')])

def dropdown_values(one):

    #Get the names of the cities out of the database
    cities = select_coordinates['Ortschaftsname']

    #Make a list with the cities, in the format that the dropdown function can read them
    cities_dropdown = []

    for city in cities:
        cities_dropdown.append({'label': city, 'value': city})

    return cities_dropdown


@app.callback(
    Output('Scatter_Temp', 'figure'),
    [Input('cities-dropdown', 'value')])
def create_graph(city):
    if city:
        # Choose the coordinate, look if a city already has been entered
        # Change the name of the city into coordinates (the data to do this is stored in the database)
        Sql_query = """SELECT Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
        # Evoke Connection
        con = database_connection.connect()
        get_coordinates = pd.read_sql(Sql_query, con=con, params=(city,))
        latitude = get_coordinates['Latitude']
        latitude = np.asarray(latitude[0])
        longitude = get_coordinates['Longitude']
        longitude = np.asarray(longitude[0])

        df = get_city_weather.get_temp(longitude, latitude)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=df.index, y=df['temperatur'].round(2), mode='markers', name="Alle Messwerte", opacity=0.6))
        fig.add_trace(
            go.Scatter(x=df.index, y=df.rolling(12).mean()['temperatur'].round(2), mode='lines',
                       name="Jahresdurchschnitt",
                       hoverinfo='skip'))

        # Define Text for Hover
        fig.update_traces(hovertemplate='Jahr: %{x} <br>Temperatur: %{y}\u00B0C')

        # plotly figure layout
        fig.update_layout(template='seaborn',
                          title={
                              'text': "Monatliche Durchschnittstemperatur",
                              'xanchor': 'right'},
                          xaxis_title='Zeit in Monaten', yaxis_title='Temperatur in \u00B0C', legend=dict(x=0, y=-0.3))

        # Close DB connection
        con.close()

    else:
        fig = go.Figure()

    return fig


@app.callback(
    Output('Change_Temp', 'figure'),
    [Input('cities-dropdown', 'value')])
def create_graph(city):
    if city:
        # Choose the coordinate, look if a city already has been entered
        # Change the name of the city into coordinates (the data to do this is stored in the database)
        Sql_query = """SELECT Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
        # Evoke Connection
        con = database_connection.connect()
        get_coordinates = pd.read_sql(Sql_query, con=con, params=(city,))
        latitude = get_coordinates['Latitude']
        latitude = np.asarray(latitude[0])
        longitude = get_coordinates['Longitude']
        longitude = np.asarray(longitude[0])

        df = get_city_weather.get_temp(longitude, latitude)
        df['temperatur'] = df['temperatur'] - float(df.mean())

        # Group by value per year
        df = df.groupby(df.index.map(lambda x: x.year)).mean()

        # start graph
        fig = go.Figure()

        pos_value = df[(df >= 0).all(axis=1)]
        neg_value = df[(df < 0).all(axis=1)]

        fig.add_trace(go.Bar(x=pos_value.index, y=round(pos_value['temperatur'], 2),
                             marker_color='crimson',
                             name=''
                             ))
        fig.add_trace(go.Bar(x=neg_value.index, y=round(neg_value['temperatur'], 2),
                             marker_color='blue',
                             name=''
                             ))
        fig.update_traces(hovertemplate='Jahr: %{x} <br>Temperaturabweichung: %{y}\u00B0C')

        # plotly figure layout
        fig.update_layout(template='plotly_white', showlegend=False,
                          title="Zeitliche Entwicklung von der Temperatur <br>(Abweichung vom Durchschnitt 1961-2020)",
                          xaxis_title='Jahre', yaxis_title='Abweichung in \u00B0C')

        # Close DB connection
        con.close()

    else:
        fig = go.Figure()

    return fig


# Display the graph of a city
@app.callback(
    Output('Scatter_Prec', 'figure'),
    [Input('cities-dropdown', 'value')])
def create_graph(city):
    if city:
        # Choose the coordinate, look if a city already has been entered
        # Change the name of the city into coordinates (the data to do this is stored in the database)
        Sql_query = """SELECT Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
        # Evoke Connection
        con = database_connection.connect()
        get_coordinates = pd.read_sql(Sql_query, con=con, params=(city,))
        latitude = get_coordinates['Latitude']
        latitude = np.asarray(latitude[0])
        longitude = get_coordinates['Longitude']
        longitude = np.asarray(longitude[0])

        df = get_city_weather.get_precipitation(longitude, latitude)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=df.index, y=df['Niederschlag'].round(2), mode='markers', name="Alle Messwerte", opacity=0.6))
        fig.add_trace(go.Scatter(x=df.index, y=df.rolling(12).mean()['Niederschlag'].round(2), mode='lines',
                                 name="Jahresdurchschnitt"))


        # Adjust Hover Text
        fig.update_traces(hovertemplate='Jahr: %{x} <br>Niederschlag: %{y}mm')

        # plotly figure layout
        fig.update_layout(template='seaborn',
                          title={
                              'text': "Monatlicher Niederschlag",
                              'xanchor': 'right'},
                          xaxis_title='Zeit in Monaten', yaxis_title='Niederschlag in mm', legend=dict(x=0, y=-0.3))

        # Close DB connection
        con.close()

    else:
        fig = go.Figure()

    return fig


@app.callback(
    Output('Change_Prec', 'figure'),
    [Input('cities-dropdown', 'value')])
def create_graph(city):
    if city:
        # Choose the coordinate, look if a city already has been entered
        # Change the name of the city into coordinates (the data to do this is stored in the database)
        Sql_query = """SELECT Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
        # Evoke Connection
        con = database_connection.connect()
        get_coordinates = pd.read_sql(Sql_query, con=con, params=(city,))
        latitude = get_coordinates['Latitude']
        latitude = np.asarray(latitude[0])
        longitude = get_coordinates['Longitude']
        longitude = np.asarray(longitude[0])

        df = get_city_weather.get_precipitation(longitude, latitude)

        df['Niederschlag'] = df['Niederschlag'] - float(df.mean())

        # Group by value per year
        df = df.groupby(df.index.map(lambda x: x.year)).sum()

        # start graph
        fig = go.Figure()

        pos_value = df[(df >= 0).all(axis=1)]
        neg_value = df[(df < 0).all(axis=1)]

        fig.add_trace(go.Bar(x=pos_value.index, y=round(pos_value['Niederschlag'], 2),
                             marker_color='crimson',
                             name=''
                             ))
        fig.add_trace(go.Bar(x=neg_value.index, y=round(neg_value['Niederschlag'], 2),
                             marker_color='blue',
                             name=''
                             ))
        fig.update_traces(hovertemplate='Jahr: %{x} <br>Abweichung: %{y}mm')

        # plotly figure layout
        fig.update_layout(template='plotly_white', showlegend=False,
                          title="Zeitliche Entwicklung vom Niederschlag <br>(Abweichung vom Durchschnitt 1961-2020)",
                          xaxis_title='Jahre', yaxis_title='Abweichung in mm')

        # Close DB connection
        con.close()

    else:
        fig = go.Figure()

    return fig

# Run the code in the browser
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8050)

