import netCDF4 as nc
import requests
from bs4 import BeautifulSoup
import urllib
import pandas as pd

#function to get average density for given region
def get_density(data,area,latitude,longitude,depth):
    density = 0
    total_vol = 0 
    for lat in latitude:
        for long in longitude:
            for dep in range(len(depth)):
                if data[dep][lat][long] > 0:     
                    density += data[dep][lat][long] * area[dep][lat][long]
                    total_vol += area[dep][lat][long]
    return density/total_vol

#function to access individual url and convert to usable netcdf object
def access_url(url):
    
    #mini-script to process large imported file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        chunks = []  # Initialize an empty list to store the fetched chunks
    
        # Fetch the data in chunks
        for chunk in response.iter_content(chunk_size=4096):
            chunks.append(chunk)  # Store the fetched chunk in the list
    
        # Concatenate the chunks to reconstruct the original NetCDF file
        complete_file = b''.join(chunks)  # Use b''.join() for binary data or ''.join() for text data
    else:
        print('Error: Unable to fetch data from the URL.')    
    # Create a NetCDF Dataset object from the in-memory buffer.
    data_nc = nc.Dataset("anynamehere", memory=complete_file)
    return data_nc

#function used to save extracted data into csv
def save_data(data_lists,titles,filename):#format:([x,y,...], [x title, y title, ...], filename)
    data={}
    # Combine the arrays using zip()
    for i in range(len(data_lists)):
        data[titles[i]] = data_lists[i]
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print("data successfully saved as ", filename)
    

# URL of the website + preprocessing to find all files links
url = 'https://portal.nccs.nasa.gov/datashare/modelE_ocean/E213SSP245/'
box_url = urllib.request.urlopen(url).read()
box_soup = BeautifulSoup(box_url,'lxml')
folders = box_soup.find('tbody').find_all('a')[1:]
all_densities = []
all_years = []
titles = ["Years"]

for ensemble in folders:
    ensemble_name = ensemble.text
    box_url_temp = urllib.request.urlopen(url+ensemble_name).read()
    box_soup_temp = BeautifulSoup(box_url_temp,'lxml')
    
    #get links to individual files, split by type
    oijl_files=[]
    for element in box_soup_temp.find_all('td', class_='link')[1:][::2]:
        oijl_files.append(element.find('a').get('href'))
    
    ojl_files=[]
    for element in box_soup_temp.find_all('td', class_='link')[2:][::2]:
        ojl_files.append(element.find('a').get('href'))

    #iterate through list to get data from all files
    years = []
    density = []
    
    #pick latitude
    lat = [130,170]#[40,80]
    long = [79,143]#[-80,0]
    for file in oijl_files:
        #get year from file name
        year = file[3:7]
        # if year == 2101:
        #     break
        years.append(year)
        print("year:",year)#checking progress, can be removed
        
        #get complete file path from portal + file name
        complete_url = url + ensemble_name + file
        data = access_url(complete_url)
        
        den = data.variables['pot_dens'] #[depth][lat][long]
        area = data.variables['oxyp3']
        depth = data.variables['zoce']
        
        temp = get_density(den,area,lat,long,depth)
        density.append(temp)
        print("value:", temp)#for progress-checking purposes
        
        
    all_densities.append(density)
    titles.append(ensemble_name[:-1])
    all_years = years
    

# File path for saving the CSV file
filename = 'DENvsTIME.csv'

# next function used in testing to save data to avoid rerunning extraction
save_data([all_years]+all_densities,titles,filename)
