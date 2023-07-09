import netCDF4 as nc
import requests
from bs4 import BeautifulSoup
import urllib
import pandas as pd

SSP245 = 'https://portal.nccs.nasa.gov/datashare/modelE_ocean/E213SSP245/'

# Function to get max at a given latitude
# Input: 
def get_max(data,latitude):
    lat = latitude + 90
    maximum = 0
    for depth in range(len(data)):
        maximum = max(maximum,data[depth][lat])
    return maximum

# Function to get average density for given region
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

# Function to access individual url and convert to usable netcdf object
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
    data_nc = nc.Dataset("temp", memory=complete_file)
    return data_nc

#function used to save extracted data into csv. NOTE: if appeneded to existing, there cannot be years in new data that are not in old data. To fix this, put all relevant years in starting csv an/or pd dataframe
def save_data(data_lists,titles,filename,mode):#format:([x,y,...], [x title, y title, ...], filename, mode: 'n' = create new file, 'a' = append to existing file)
    data={}
    # Combine the arrays using zip()
    for i in range(len(data_lists)):
        data[titles[i]] = data_lists[i]
        print(titles[i])
    
    if mode=='a':
        #make new pandas dataframe and get list of relevant columns
        df_new = pd.DataFrame(data)
        new_columns = df_new.columns.tolist()#.remove("Years")
        new_columns.remove('Years')
        
        #get old pandas dataframe and get list of relevant columns
        df_old = pd.read_csv(filename)
        old_columns = df_old.columns.tolist()#.remove("Years")
        old_columns.remove('Years')
        
        #find dups in columns
        duplicate_columns = set(old_columns) & set(new_columns)

        #if there is duplicate columns, fill NaNs
        #else, merge dataframes
        if duplicate_columns:
            for col in duplicate_columns:
                df_old[col].fillna(df_new[col], inplace=True)
            df_old.to_csv(filename,index=False)
        else:    
            merged = pd.merge(df_old,df_new,on = 'Years',how = 'outer')
            merged.to_csv(filename, index=False)
    elif mode =='n':
        df_new = pd.DataFrame(data)
        df_new.to_csv(filename, index=False)
        pass
    else:
        print('Error: Invalid Mode')
        return None
    print("data successfully saved as", filename)
    return None
 
# Function to get files from portal url where files are in parent 1 folders
def get_files(url):#file types: 'oijl', 'oij', 'ojl', 'other'| returns dict[ensemble][file type]
    # Get url and access html code
    box_url = urllib.request.urlopen(url).read()
    box_soup = BeautifulSoup(box_url,'lxml')
    folders = box_soup.find('tbody').find_all('a')[1:]
    # Make output dictionary
    output = {}
    # Get files names and organize in dictionary
    for ensemble in folders:
        ensemble_name = ensemble.text
        time_scales = ["Annual", "Monthly"]
        dict_ts={}
        for time_scale in time_scales:
            box_url_temp = urllib.request.urlopen(url+ensemble_name+time_scale+'/').read()
            box_soup_temp = BeautifulSoup(box_url_temp,'lxml')
            
            # Get links to individual files, split by type
            all_files = box_soup_temp.find_all('td', class_='link')[1:]
            oijl_files=[]
            ojl_files=[]
            oij_files=[]
            other_files = []
            for element in all_files:
                file = element.text[8:12]
                if file == 'oijl':
                    oijl_files.append(element.text)
                elif file[:-1] == 'oij':
                    oij_files.append(element.text)
                elif file[:-1] == 'ojl':
                    ojl_files.append(element.text)
                else:
                    other_files.append(element.text)
            dict_ts[time_scale] = {'oijl':oijl_files, 'ojl':ojl_files, 'oij':oij_files, 'other':other_files}
        output[ensemble_name[:-1]] = {'Annual':dict_ts['Annual'], 'Monthly': dict_ts['Monthly']}
    return output

