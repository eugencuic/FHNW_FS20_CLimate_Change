import pandas as pd
import numpy.ma as ma
from netCDF4 import Dataset
import os
from bs4 import BeautifulSoup
import requests

def get_location():

    #Get the current IP adress of the user
    page = requests.get("https://iplocation.com/")
    soup = BeautifulSoup(page.content, 'html.parser')

    #ip_adress = soup.find("b").get_text()
    lattitude = soup.find("td", {"class": "lat"}).get_text()
    longitude = soup.find("td", {"class": "lng"}).get_text()
    return(float(longitude), float(lattitude))


#Funktion um die Temperatur an einer Koordinate zu erhalten
def get_temp (lon_location, lat_location):

    def find_temperatur(year,min_index_lon,min_index_lat):

        #open file
        path = os.path.join(os.path.expanduser('~'), 'climate_change', 'TabsM_1961_2017_ch01r.swisscors', 'TabsM_ch01r.swisscors_{Y}01010000_{Y}12010000.nc').format(Y=year)
        meteoswiss_data = Dataset(path)

        #creating a List and adding the Value of the same messurment point to it
        
        timeseries = []
        temperatur = meteoswiss_data.variables['TabsM']

        for month in range(0,12):
            timeseries.append(temperatur[month][min_index_lat][min_index_lon])
        #close netcdf
        meteoswiss_data.close()
        
        return(timeseries)

    path = os.path.join(os.path.expanduser('~'), 'climate_change', 'TabsM_1961_2017_ch01r.swisscors', 'TabsM_ch01r.swisscors_{Y}01010000_{Y}12010000.nc').format(Y=1961)
    meteoswiss_data = Dataset(path)

    # read latitutde and longitude variable
    lat = meteoswiss_data.variables['lat'][:] 
    lon = meteoswiss_data.variables['lon'][:]

    #calculate the min distance of a measurement station
    sq_distance = ((lat_location-lat)**2)+((lon_location-lon)**2)

    #find the index of the array with the smallest distance
    index = ma.where(sq_distance == sq_distance.min())
    min_index_lat = index[0][0]
    min_index_lon = index[1][0]

    #close netcdf
    meteoswiss_data.close()

    # create a List to put the Temperature values in.
    temperatur_year = []

    for year in range(1961, 2020):
        temperatur_year = temperatur_year + find_temperatur(year, min_index_lon, min_index_lat)

    # creating a panda with the temperature for the city
    data_range = pd.date_range(start='1961', end='2020', freq='M')
    timeseries_temp = pd.DataFrame(temperatur_year, columns=['temperatur'], index=data_range)
    return (timeseries_temp)


#Funktion um den Niederschlag in einer Koordinate zu erhalten
def get_precipitation (lon_location, lat_location):


    def find_precipitation(year,min_index_lon,min_index_lat):

        #open file
        path = os.path.join(os.path.expanduser('~'), 'climate_change', 'RhiresM_1961_2019_ch01r.swisscors', 'RhiresM_ch01r.swisscors_{Y}01010000_{Y}12010000.nc').format(Y=year)

        meteoswiss_data = Dataset(path)

        #creating a List and adding the Value of the same messurment point to it
        
        timeseries = []

        precipitation = meteoswiss_data.variables['RhiresM']

        for month in range(0,12):
            timeseries.append(precipitation[month][min_index_lon][min_index_lat])
        #close netcdf
        meteoswiss_data.close()
        return(timeseries)

    path = os.path.join(os.path.expanduser('~'), 'climate_change', 'TabsM_1961_2017_ch01r.swisscors', 'TabsM_ch01r.swisscors_{Y}01010000_{Y}12010000.nc').format(Y=1961)

    meteoswiss_data = Dataset(path)

    # read latitutde and longitude variable
    lat = meteoswiss_data.variables['lat'][:] 
    lon = meteoswiss_data.variables['lon'][:]

    #calculate the min distance of a measurement station
    sq_distance = ((lat_location-lat)**2)+((lon_location-lon)**2)
    min_sq_distance = sq_distance.min()

    #find the index of the array with the smallest distance
    index = ma.where(sq_distance == sq_distance.min())
    min_index_lat = index[0][0]
    min_index_lon = index[1][0]

    #extract the precipitation for all years and saving them to a list
    precipitation_year = []
    for year in range(1961,2020):
        precipitation_year = precipitation_year + find_precipitation(year,min_index_lat,min_index_lon)

    data_range = pd.date_range(start = '1961', end= '2020', freq='M')

    #creating a panda with the precipitation for the city
    Niederschlag = pd.DataFrame(precipitation_year, columns=['Niederschlag'], index=data_range)
    return(Niederschlag)
