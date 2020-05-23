import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
from dash.dependencies import Input, Output
import pandas as pd
from pathlib import Path
import sqlalchemy
import get_city_weather
import numpy as np
import os

#Code für den Server

# Create the variables and queries required for the database connection, the actual connction will happen in the callback functions
database_username = 'climate_change'
database_password = 'FHNW_climate_20'
database_ip = 'localhost'
database_name = 'Climate_Change'

database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                               format(database_username, database_password,
                                                      database_ip, database_name))

# TODO Define a stylesheet
# Stylesheet with the pre defined styles for website layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Create a dash object
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Define the colors
colors = {
    'background': '#111111',
    'text': '#7FDBFF'}

# Define the Layout of the app
app.layout = html.Div(

    # Content of this section
    children=[

        # Header
        html.H1(
            children='Hello all',
            style={
                'textAlign': 'center'}),

        # Text
        html.Div(
            children='''Wählen Sie die gewünschte Option aus''',
            style={
                'textAlign': 'center'}),

        # Dropdown for selecting the temperatur or Precicipation
        html.Div(
            dcc.Dropdown(
                id='weather-dropdown',
                options=[{'label': 'Niederschlag', 'value': 'Niederschlag'},
                         {'label': 'Temperatur', 'value': 'Temperatur'}],
                value='Niederschlag'),
            style={
                'margin-left': 20,
                'margin-right': 20}),

        html.Div(
            children='''Wählen Sie das gewünschte Jahr aus''',
            style={
                'margin-top': 30,
                'margin-bottom': 10,
                'margin-left': 30,
                'margin-right': 30,
                'textAlign': 'center'}),

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
                       '2019': '2019'},
                updatemode='drag'),
            style={
                'margin-right': 50,
                'margin-left': 50}),

        html.Div(
            children='''Wählen Sie den gewünschten Monat aus''',
            style={
                'margin-top': 50,
                'margin-bottom': 10,
                'margin-left': 30,
                'margin-right': 30,
                'textAlign': 'center'}),

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
                       '12': 'Dezember'},
                updatemode=('drag')),
            style={
                'margin-left': 50,
                'margin-right': 50}),

        # HTML Tag where the image will show up
        html.Img(
            id='show_image',
            style={
                'width': 864,
                'height': 648,
                'margin-left': 300,
                'margin-right': 300}),

        html.Div(
            children='''Wählen Sie die gewünschte Stadt aus''',
            style={
                'margin-top': 50,
                'margin-bottom': 10,
                'margin-left': 30,
                'margin-right': 30,
                'textAlign': 'center'}),

        html.Div(
            dcc.Dropdown(
                id='cities-dropdown',
                placeholder='Wählen Sie eine Stadt',
                clearable=False),
            style={
                'margin-left': 50,
                'margin-right': 50}),

        dcc.Graph(
            id='City-Graph'),

        html.Div(
            children='Quellen')

    ])



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


#Display the graph of a city
@app.callback(
    Output('City-Graph', 'figure'),
    [Input('cities-dropdown', 'value'),
     Input('weather-dropdown', 'value')])

def create_graph(city, weather):

    if city:
        #Choose the coordinate, look if a city already has been entered
        #Change the name of the city into coordinates (the data to do this is stored in the database)
        Sql_query = """SELECT Ortschaftsname, Longitude, Latitude FROM coordinates WHERE Ortschaftsname = %s;"""
        # Evoke Connection
        con = database_connection.connect()
        get_coordinates = pd.read_sql(Sql_query, con=con, params=(city,))
        latitude = get_coordinates['Latitude']
        latitude = np.asarray(latitude[0])
        longitude = get_coordinates['Longitude']
        longitude = np.asarray(longitude[0])

        #Look if the temperature or the precipitation was choosen
        if weather == 'Niederschlag':

            #Use the function from the file get city weather in this folder to get the precipitation at this coordinate during every month since 1964
            Precipitation = get_city_weather_Dash.get_precipitation(longitude, latitude)

            #Plot the graph
            Graph = px.bar(Precipitation, x='Datum', y='Niederschlag', title = city)


        else:

            #Use the function from the file get city weather in this folder to get the temperature at this coordinate during every month since 1964
            Temperature = get_city_weather_Dash.get_temp(longitude, latitude)


            Graph = px.line(Temperature, x=Temperature.index, y=Temperature.temperatur.rolling(12).mean(), title = city)

        # Close DB connection
        con.close()

    else:
        Graph = px.line()

    return Graph

# TODO Quellenangabe

# Run the code in the browser
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8050)

