# import required modules
import geopandas as gpd
import pandas as pd

# load data from file
crime_data = gpd.read_file('data_files/NI_crimes.shp')

print(crime_data.head(10))
