from bs4 import BeautifulSoup
from sqlalchemy.sql import text
import sqlalchemy
import pandas as pd
import io
import requests
import zipfile
import mysql.connector

#Get the connection to the website
url = 'https://www.cadastre.ch/de/services/service/registry/plz.html'

#Accessing the entire website
website = requests.get(url)

#Creating a beautiful soup object with the webpage, using the html parser
soup = BeautifulSoup(website.content, 'html.parser')

#Finding the right section
section = soup.find('div', class_= 'parsys_column row')

#Finding the section with the link to the file
link = section.find('a', string = 'CSV (Excel) WGS84 ')

#Extract the link with the desired data
data_file = link['href']

#Unzip the zip file and store it in the same directory as this file is stored
get_data = requests.get(data_file)
content = zipfile.ZipFile(io.BytesIO(get_data.content))
data_folder = content.extractall()

#Load Data into Pandas DataFrame
raw_data = pd.read_csv('PLZO_CSV_WGS84/PLZO_CSV_WGS84.csv', sep=';', engine='python')

#Just take those columns that are needed
raw_data = raw_data[['Ortschaftsname', 'PLZ', 'E', 'N']]

#Rename E and N to Longtidue and Latitude for a better understanding of the data
koord_data = raw_data.rename(columns={
    'E' : 'Longitude', 
    'N' : 'Latitude'}
    )

#Replace all ä,ö,ü with ae, oe, ue
#koord_data = koord_data.replace('ä', 'ae', regex=True)
#koord_data = koord_data.replace('ö', 'oe', regex=True)
#koord_data = koord_data.replace('ü', 'ue', regex=True)

#Create Connection Engine
database_username ='climate_change'
database_password = 'FHNW_climate_20'
database_ip = 'localhost'
database_name = 'Climate_Change'

database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                               format(database_username, database_password, 
                                                      database_ip, database_name))


#Evoke Connection
con = database_connection.connect()

#Set Encoding to utf8 due to missbehaviour without
utf8 = text("""
SET NAMES 'utf8';
""")
con.execute(utf8)

#Drop all Data from Database
delet_rows = text("""
DELETE FROM Climate_Change.coordinates;
""")
con.execute(delet_rows)

#Send Data to Database
koord_data.to_sql(con=database_connection, name='coordinates', if_exists='replace')