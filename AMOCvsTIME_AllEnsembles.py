import netCDF4 as nc
import requests
from bs4 import BeautifulSoup
import urllib
import numpy
import pandas as pd

#function to get max at a given latitude
def get_max(data,latitude):
    lat = latitude + 90
    maximum = 0
    for depth in range(len(data)):
        if data[depth][lat]>maximum:
            maximum = data[depth][lat]
        #maximum = max(maximum,data[depth][lat])
        #maximum = max(maximum, data[depth, lat].item
    return maximum

#function to access individual url and convert to usable netcdf object
def access_url(url):
    data = requests.get(url).content
    # Create a NetCDF Dataset object from the in-memory buffer.
    data_nc = nc.Dataset("anynamehere", memory=data)
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
all_amocs = []
all_years = []
titles = ["Years"]
#print(folders)
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
    max_amoc = []
    #pick latitude
    latitude = 48
    for file in ojl_files:
        #get year from file name
        year = file[3:7]
        years.append(year)
        #get complete file path from poral + file name
        complete_url = url + ensemble_name + file
        #print(complete_url)
        data = access_url(complete_url)
        yearly_max = get_max(data.variables["sf_Atl"],latitude)
        #append to results array
        max_amoc.append(yearly_max)
    
        print("year:",year,"ensemble:", ensemble_name)#checking progress, can be removed
    all_amocs.append(max_amoc)
    titles.append(ensemble_name[:-1])
    if all_years != years:
        print("ERROR")
    all_years = years

# File path for saving the CSV file
filename = 'AMOCvsTIME_lat48AllEnsembles.csv'

# next function used in testing to save data to avoid rerunning extraction
save_data([all_years] + all_amocs,titles,filename)