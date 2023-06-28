import netCDF4 as nc
import requests
from bs4 import BeautifulSoup
import urllib
import csv

#function to get max at a given latitude
def get_max(data,latitude):
    lat = latitude + 90
    maximum = 0
    for depth in range(len(data)):
        maximum = max(maximum,data[depth][lat])
    return maximum

#function to access individual url and convert to usable netcdf object
def access_url(url):
    data = requests.get(url).content
    # Create a NetCDF Dataset object from the in-memory buffer.
    data_nc = nc.Dataset("anynamehere", memory=data)
    return data_nc

#function used to save extracted data into csv
def save_data(x,y,x_title,y_title,filename):
    
    # Combine the arrays using zip()
    data = zip(x,y)
    
    # Open the file in write mode
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the data to the CSV file
        writer.writerow([x_title, y_title])  # Write header row
        writer.writerows(data)
    print("data successfully saved as ", filename)
    

# URL of the website + preprocessing to find all files links
url = 'https://portal.nccs.nasa.gov/datashare/modelE_ocean/E213SSP245/SSP245a/'
box_url = urllib.request.urlopen(url).read()
box_soup = BeautifulSoup(box_url,'lxml')

#get links to individual files, split by type
oijl_files=[]
for element in box_soup.find_all('td', class_='link')[1:][::2]:
    oijl_files.append(element.find('a').get('href'))

ojl_files=[]
for element in box_soup.find_all('td', class_='link')[2:][::2]:
    ojl_files.append(element.find('a').get('href'))

#iterate through list to get data from all files
years = []
max_amoc = []
#pick latitude
latitude = 26
for file in ojl_files:
    #get year from file name
    year = file[3:7]
    years.append(year)
    #get complete file path from poral + file name
    complete_url = url + file
    data = access_url(complete_url)
    yearly_max = get_max(data.variables["sf_Atl"],latitude)
    #append to results array
    max_amoc.append(yearly_max)
    
    print("year:",year,"value:", yearly_max)#checking progress, can be removed
    

# File path for saving the CSV file
filename = f'AMOCvsTIME_lat{latitude}.csv'

# next function used in testing to save data to avoid rerunning extraction
save_data(years,max_amoc,"Years","AMOC",filename)