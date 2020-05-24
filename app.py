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
                                html.H1(
                                    'Webseite des Projektes Climate Change des Studienganges Data Science der FHNW',
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
                                dcc.Markdown(
                                    'Auf dieser Webseite finden Sie Grafiken, welche den Klimawandel visualisieren und auf welcher Sie'
                                    'Informationen über das Klima in der Schweiz finden können. '
                                    'Speziell richtet sich diese Seite an Weinbauern oder Personen die sich für Wein interessieren und welche'
                                    'Auswirkungen das Klima auf Weintrauben hat. '
                                    ''
                                    'Im folgenden wird die Auswirkung der Klimaveränderung auf den Wein/Weintrauben kurz beschrieben.',
                                    style={
                                        'margin': 20
                                    }
                                )
                            )
                        ]
                    ),
                ]
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
                                    'Wählen Sie aus, ob Sie mehr über den Niederschlag oder die Temperatur in der Schweiz wissen möchten.'
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
                        ], width=8
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    'Wählen Sie aus, von welchem Jahr Sie die Temperatur oder den Niederschlag in der Schweiz wissen möchten.'
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
                            # Slider for selecting the month
                            html.Div(
                                dcc.Slider(
                                    id='month-slider',
                                    min=1,
                                    max=12,
                                    value=1,
                                    step=1,
                                    marks={'1': 'Januar',
                                           '2': 'Februar',
                                           '3': 'März',
                                           '4': 'April',
                                           '5': 'Mai',
                                           '6': 'Juni',
                                           '7': 'Juli',
                                           '8': 'August',
                                           '9': 'September',
                                           '10': 'Oktober',
                                           '11': 'November',
                                           '12': 'Dezember'
                                           },
                                    updatemode=('drag')
                                )
                            )
                        ], width=8
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    'Wählen Sie aus, für welchen Monat in oben gewähltem Jahr Sie die Temperatur oder der Niederschlag interessiert.'
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
                                dcc.Markdown(
                                    'Auf der Karte unten, finden Sie das ausgewählte Wetter (Temperatur oder Niederschlag) visualisiert über '
                                    'der ganzen Schweiz, für den Monat und das Jahr, welches Sie ausgewählt haben.'
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
                ]
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
                                    'Wählen Sie eine Gemeinde aus, für welche Sie der Verlauf der Temperatur und der Niederschlagmenge '
                                    'während des Jahres 1961 bis 2019 interessiert.'
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
                               html.H2(
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
                        ], width=10
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    'Hier ist die Erklärung zum ersten Plot'
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
                        width=10
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    'Hier ist die Erklärung zum zweiten Plot'
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
                                dcc.Graph(
                                    id='Scatter_Prec'
                                )
                            )
                        ],
                        width=10
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    'Hier ist die Erklärung zum dritten Plot'
                                )
                            )
                        ]
                    )
                ],
                style={
                    'margin': 10
                }
            ),            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Graph(
                                    id='Change_Prec'
                                )
                            )
                        ],
                        width=10
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Markdown(
                                    'Hier ist die Erklärung zum vierten Plot'
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
                                dcc.Markdown(
                                    'Quellenangaben'
                                )
                            )
                        ]
                    ),
                ],
                style={
                    'margin': 20
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

    # Evoke Connection
    con = database_connection.connect()

    # Select the needed columns and put them in a pandas dataframe
    select_coordinates = pd.read_sql('SELECT Ortschaftsname, Longitude, Latitude FROM coordinates', con=con)

    #Get the names of the cities out of the database
    cities = select_coordinates['Ortschaftsname']

    #Make a list with the cities, in the format that the dropdown function can read them
    cities_dropdown = []

    for city in cities:
        cities_dropdown.append({'label': city, 'value': city})

    # Close the database connection
    con.close()

    return cities_dropdown


@app.callback(
    Output('Scatter_Temp', 'figure'),
    [Input('cities-dropdown', 'value')])
def create_graph(city):
    if city:
        # Choose the coordinate, look if a city already has been entered
        # Change the name of the city into coordinates (the data to do this is stored in the database)
        Sql_query = """SELECT Ortschaftsname, Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
        # Evoke Connection
        con = database_connection.connect()
        get_coordinates = pd.read_sql(Sql_query, con=con, params=(city,))
        latitude = get_coordinates['Latitude']
        latitude = np.asarray(latitude[0])
        longitude = get_coordinates['Longitude']
        longitude = np.asarray(longitude[0])

        df = get_city_weather.get_temp(longitude, latitude)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['temperatur'], mode='markers', name="Alle Messwerte"))
        fig.add_trace(
            go.Scatter(x=df.index, y=df.rolling(12).mean()['temperatur'], mode='lines', name="Jahresdurchschnitt",
                       hoverinfo='skip'))

        # trend Line von scatter berechnen
        help_fig = px.scatter(df, x=df.index, y=df["temperatur"],  trendline="ols")
        x_trend = help_fig["data"][1]['x']
        y_trend = help_fig["data"][1]['y']

        # Linie hinzufügen
        fig.add_trace(go.Line(x=x_trend, y=y_trend, name="Trendlinie"))


        # Define Text for Hover
        fig.update_traces(hovertemplate='Jahr: %{x} <br>Temperatur: %{y}\u00B0C')

        # plotly figure layout
        fig.update_layout(template='seaborn',
                          title="Monatliche Durchschnittstemperatur",
                          xaxis_title='Zeit in Monaten', yaxis_title='Temperatur in \u00B0C')

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
        Sql_query = """SELECT Ortschaftsname, Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
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

        fig.add_trace(go.Bar(x=pos_value.index, y=pos_value['temperatur'],
                             marker_color='crimson',
                             name=''
                             ))
        fig.add_trace(go.Bar(x=neg_value.index, y=neg_value['temperatur'],
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
        Sql_query = """SELECT Ortschaftsname, Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
        # Evoke Connection
        con = database_connection.connect()
        get_coordinates = pd.read_sql(Sql_query, con=con, params=(city,))
        latitude = get_coordinates['Latitude']
        latitude = np.asarray(latitude[0])
        longitude = get_coordinates['Longitude']
        longitude = np.asarray(longitude[0])

        df = get_city_weather.get_precipitation(longitude, latitude)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Niederschlag'], mode='markers', name="Alle Messwerte"))
        fig.add_trace(go.Scatter(x=df.index, y=df.rolling(12).mean()['Niederschlag'], mode='lines', name="Jahresdurchschnitt"))

        # trend Line von scatter berechnen
        help_fig = px.scatter(df, x=df.index, y="Niederschlag",  trendline="ols")
        x_trend = help_fig["data"][1]['x']
        y_trend = help_fig["data"][1]['y']

        # Linie hinzufügen
        fig.add_trace(go.Line(x=x_trend, y=y_trend, name="Trendlinie", ))


        # Adjust Hover Text
        fig.update_traces(hovertemplate='Jahr: %{x} <br>Niederschlag: %{y}mm')

        # plotly figure layout
        fig.update_layout(template='seaborn',
                          title="Monatlicher Niederschlag",
                          xaxis_title='Zeit in Monaten', yaxis_title='Niederschlag in mm')

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
        Sql_query = """SELECT Ortschaftsname, Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
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

        fig.add_trace(go.Bar(x=pos_value.index, y=pos_value['Niederschlag'],
                             marker_color='crimson',
                             name=''
                             ))
        fig.add_trace(go.Bar(x=neg_value.index, y=neg_value['Niederschlag'],
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

# TODO Quellenangabe

# Run the code in the browser
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8050)

