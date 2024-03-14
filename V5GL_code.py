#!/usr/bin/env python
# coding: utf-8

# Libraries
from scipy.io import netcdf
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from numpy import dtype
import pandas as pd
import geopandas as gpd
import xarray as xr

# data source:
data_html = 'https://sites.wustl.edu/acag/datasets/surface-pm2-5/' #pm2.5
geojson_html = 'https://gadm.org/download_country.html' #gadm

#====================================
# open a netCDF and geojson file
# change the code here
#====================================

filename = "INSERT_NC_FILE_LOCATION"
geojson_file = 'INSERT_GEOJSON_FILE_LOCATION'

# This code merges the pm2.5 data to administrative geojson data.

#====================================
#  No need to change codes after this 
#====================================

#====================================
#  Working on netCDF data 
#====================================
print("Working on netCDF pm2.5 data")

ncin = Dataset(filename, 'r', format='NETCDF4')

pm25 = ncin.variables['GWRPM25'][:]
lat = ncin.variables['lat'][:]
lon = ncin.variables['lon'][:]

# Assuming you have already loaded the data into pm25, lat, and lon arrays

# Create xarray DataArray objects
pm25_da = xr.DataArray(pm25, dims=('lat', 'lon'),
                       coords={'lat': lat, 'lon': lon})
lat_da = xr.DataArray(lat, dims=('lat',), coords={'lat': lat})
lon_da = xr.DataArray(lon, dims=('lon',), coords={'lon': lon})

# Create an xarray Dataset
dataset = xr.Dataset({'pm25': pm25_da, 'lat': lat_da, 'lon': lon_da})

# Convert xarray Dataset to pandas DataFrame
df = dataset.to_dataframe()

# Reset index to convert MultiIndex to regular columns
df_reset = df.reset_index()

# Melt the DataFrame to long form
df_long = df_reset.melt(id_vars=['lat', 'lon'],
                        var_name='variable', value_name='value')

print("Finished importing netCDF pm2.5 data")

#====================================
#  Read in the GeoJSON file 
#====================================

print("Working on geojson data")

gdata = gpd.read_file(geojson_file)

# copy only NAME_1 and geometry columns
gdata_truc = gdata[['NAME_1', 'geometry']]
gdata_truc

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(gdata_truc)

# Define lists to store latitudes and longitudes
lats = []
lons = []
names = []  # List to store repeated NAME_1 values

# Iterate through each row
for index, row in gdf.iterrows():
    # Get the geometry
    geometry = row['geometry']
    name = row['NAME_1']  # Get the NAME_1 value for the row
    # If it's a MultiPolygon, iterate through its constituent polygons
    if geometry.geom_type == 'MultiPolygon':
        for polygon in geometry.geoms:
            # Extract coordinates
            coords = polygon.exterior.coords
            # Separate latitudes and longitudes
            latitudes = [coord[1] for coord in coords]
            longitudes = [coord[0] for coord in coords]
            # Extend the lists
            lats.extend(latitudes)
            lons.extend(longitudes)
            # Repeat NAME_1 for the corresponding number of coordinates
            names.extend([name] * len(latitudes))
    # If it's a Polygon, extract coordinates directly
    elif geometry.geom_type == 'Polygon':
        coords = geometry.exterior.coords
        latitudes = [coord[1] for coord in coords]
        longitudes = [coord[0] for coord in coords]
        lats.extend(latitudes)
        lons.extend(longitudes)
        names.extend([name] * len(latitudes))

# Create a DataFrame for latitudes, longitudes, and repeated names
coordinates_df = pd.DataFrame(
    {'NAME_1': names, 'lat': lats, 'lon': lons})

# return the unique values in the NAME_1 column
unique_names = coordinates_df['NAME_1'].unique()

# loop through the unique names, return the max and min values of the lat and lon columns
# and save them in a new DataFrame

# Create an empty list to store the results
results = []

# Iterate through the unique names
for name in unique_names:
    # Get the subset of the DataFrame for the current name
    subset = coordinates_df[coordinates_df['NAME_1'] == name]
    # Get the maximum and minimum latitudes and longitudes
    max_lat = subset['lat'].max()
    min_lat = subset['lat'].min()
    max_lon = subset['lon'].max()
    min_lon = subset['lon'].min()
    # Append the results as a dictionary to the list
    results.append({'NAME_1': name, 'max_lat': max_lat, 'min_lat': min_lat,
                    'max_lon': max_lon, 'min_lon': min_lon})

# Convert the list of dictionaries to a DataFrame
results_df = pd.DataFrame(results)

print("Finished importing geojson data")

#====================================
#  Merged NetCDF data to the Geojson  
#====================================

print("Start adding pm2.5 to geojson data")

# if the lat and lon values are within the range of the max and min values of the lat and lon columns
# then return the mean of all non-empty values in the value column of df_long and add it to the results_df

# Create an empty list to store the results
final_results = []

# Iterate through the rows of the results DataFrame
for index, row in results_df.iterrows():
    # Get the name, max_lat, min_lat, max_lon, and min_lon values
    name = row['NAME_1']
    max_lat = row['max_lat']
    min_lat = row['min_lat']
    max_lon = row['max_lon']
    min_lon = row['min_lon']
    # Get the subset of the DataFrame for the current name
    subset = df_long[(df_long['lat'] <= max_lat) & (df_long['lat'] >= min_lat) &
                     (df_long['lon'] <= max_lon) & (df_long['lon'] >= min_lon)]
    # Calculate the mean of the non-empty values in the 'value' column
    mean_value = subset['value'].mean()
    # Append the results as a dictionary to the list
    final_results.append({'NAME_1': name, 'mean_pm25': mean_value})

# Convert the list of dictionaries to a DataFrame
final_results_df = pd.DataFrame(final_results)

# export to csv
# final_results_df.to_csv('final_results.csv', index=False)


# add the 'mean_pm25' to the gdata DataFrame. This is your desired results.
gdata_pm = gdata.merge(final_results_df, on='NAME_1')
print("FINISHED")

#===========================================
#  plot the mean_pm25 values on the map  
#===========================================
 
# gdata_pm.plot(column='mean_pm25', legend=True, figsize=(15, 10))
# plt.show()
