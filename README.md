# Merra Download Script
This Python script downloads, cleans, and aggregates meteorological data from NASA's MERRA-2 database. It is adapted from https://github.com/Open-Power-System-Data/weather_data/blob/master/download_merra2.ipynb. There are three steps to execution: 1) Setting up a data access account with MERRA-2 and obtaining a username and password, 2) Inputing the fields, years, and locations desired, 3) Running the script. Each step is described in detail below. The outputs of the script are three separate CSV files, the first aggregated by hour, the second by day, and the third by week.

### Dependencies
- Python 3 - download from https://www.python.org/downloads/
- numpy (download via command line with `pip install numpy`)
- pandas (download via command line with `pip install pandas`)
- xarray (download via command line with `pip install xarray`)
- dateutil (download via command line with `pip install python-dateutil`)

### 1) Setting up a data access account with MERRA-2
1. Register an account at https://urs.earthdata.nasa.gov/. Note your username and password for inputting in the script.
2. Visit "Applications" --> "Authorized Apps" and click "Approve More Applications". 
3. Add "NASA GESDISC DATA ARCHIVE" for approval (you will have to scroll down the list).

### 2) Add inputs to the script specifying which data to download
The first section of the script (following the imports) is the only section you will have to change. It contains the specifics of the data you will download, which you will have to input. 
1. In the `username` and `password` variables, input your username and password for MERRA-2 access
2. In the `years` variable, input the years you would like to download data for, in the format of a list of integers (for example, [2010, 2011, 2012]).
3. In the `field_id` variable, input the field ID for the meteorological field you would like to download (for purposes of aggregation, the script can only download one field at a time). You can look up ID's for different fields at https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf. Examples include  `'T2M'` (temperature at 2 meters), `'QV2M'` (humidity), and `'SPEEDLML'` (windspeed). Important note: Only fields that are recorded hourly can be downloaded with this script. The recording frequency is also noted in the specification document.
4. In the `field_name` variable, write down a name for the meteorological field you will download. It need not be the same name provided in the MERRA specification, it will only be used to label the data once it is downloaded.
5. In the `database_name` variable, input the name of the specific database within MERRA from which the data will be downloaded. These database names can also be looked up at https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf. Examples include `'M2I1NXASM'` and `'M2T1NXLND'`.
6. In the `database_id` variable, input the ID of the specific database within MERRA rom which the data will be downloaded, again accessed from https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf. Examples include `'tavg1_2d_lnd_Nx'` and `'inst1_2d_asm_Nx'`. The database ID and database name are both useful unique identifiers for the database.
7. In the `locs` variable, input a list of locations for which the data will be downloaded. Each location is a three-tuple, where the first part is a string (the name of the location, which does not correspond to any value in MERRA but will be used to label your data), the longitude, and the latitude (each of which are floats). An example of a single location is `('Maputo', -25.9629, 32.5732)`. 
8. In the `conversion_function` variable, input a function that will be used to convert the hourly data downloaded from the units used by MERRA to the units you would like to use it your analysis. This is a lambda function, in the form of `lambda x: f(x)`, where `f` is your function. Examples include:
- `lambda x: x - 273.15` (for converting temperature data in Kelvin to Celsius)
- `lambda x: x * 3600` (for converting precipitation data in mm/s to mm/hour)
- `lambda x: x` (if no conversion is desired)
9. In the `aggregator` variable, input the method that should be used for aggregation across hours and days. Options include `'mean'`, `'sum'`, `'max'`, and `'min'`. For example, precipitation data is recorded in MERRA in mm, and should be aggregated by `'sum'` for total rainfall. Temperature data should be aggregated by `'mean'` to optain the average daily or weekly temperature, or by `'max'` to obtain the daily and weekly high temperature.

### 3) Run the script
Run the script via the command line by running `python merra_scraping.py` in the script's home directory. 

The script runs in two parts: first, it downloads data from MERRA, then it cleans and aggregates the data. The first part takes around 6 minutes per location per year, while the second takes around 0.1 minutes per location per year. The script will keep you updated via outputs to the command line as it progresses, including time estimates for each part. If there are any issues downloaded certain files, the script will also notify you of these via command line outputs.

The outputs of the script is a folder, named for the meteorolical field downloaded, which will appear in the script's home directory. Within this folder will be sub-folders for each location downloaded, which contain the raw .nc4 files downloaded from MERRA. Also within the folder labeled with the field name will be hourly, daily, and weekly CSV files for each location scraped (labeled as location_hourly.csv, location_daily.csv, and location_weekly.csv). These files should be used for future analysis.




