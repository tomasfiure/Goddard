import netCDF4 as nc
import numpy as np
import pandas as pd
import goddard as gd
   

# URL of the website + preprocessing to find all files links
url = 'https://portal.nccs.nasa.gov/datashare/modelE_ocean/E213SSP245/'
all_densities = []
all_years = []
titles = ["Years"]
files = gd.get_files(url)
for ensemble in files.keys():
    #iterate through list to get data from all files
    years = []
    density = []
    #pick latitude
    lat = [130,170]#[40,80]
    long = [79,135]#[-80=79,0=143]
    for file in files[ensemble]['Annual']['oijl']:
        #get year from file name
        year = file[3:7]
        years.append(year)
        print("year:",year)#checking progress, can be removed
        #get complete file path from portal + file name
        complete_url = url + ensemble + '/Annual/'+ file
        data = gd.access_url(complete_url)
        
        den = data.variables['pot_dens'] #[depth][lat][long]
        area = data.variables['oxyp3']
        depth = data.variables['zoce']
        
        temp = gd.get_density(den,area,lat,long,depth)
        data.close()
        density.append(temp)
        print("value:", temp)#for progress-checking purposes
        
        
    all_densities.append(density)
    titles.append(ensemble)
    all_years = years
    

# File path for saving the CSV file
filename = 'DENvsTIME_2.csv'

# next function used in testing to save data to avoid rerunning extraction
gd.save_data([all_years]+all_densities,titles,filename)
