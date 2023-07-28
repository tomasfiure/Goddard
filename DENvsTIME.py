import netCDF4 as nc
import numpy as np
import pandas as pd
import goddard as gd
import os
import time
import pickle

def save_array(folder_path,array,info):
    file_name = info[1]+'.nc'
    file_path = folder_path+'\\'+info[0]+'\\'+file_name
    with nc.Dataset(file_path, 'w') as new_nc:
        dim1, dim2, dim3 = array.shape
        new_nc.createDimension('lat', dim1)
        new_nc.createDimension('lono', dim2)
        new_nc.createDimension('depth', dim3)
        new_var = new_nc.createVariable(info[0], 'f4', ('lat', 'lono', 'depth'))
        new_var[:] = array[:]


def den_from_web():
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

def den_from_local(folder_path):
    # Ensembles Used
    ensembles = ['SSP245a', 'SSP245c', 'SSP245g', 'SSP245i']
    # Make dict to store data, which will be made into pandas dataframe
    temp_dict = {}
    
    # Region Title
    regions = 'Irm_Lab' 
    # Depth of choice
    depth = '500m'
    # Pick rectangular regions for data analysis
    region = gd.pick_region(regions,depth)
    
    # Iterate thorugh ensembles
    for ensemble in ensembles:
        tim = 0
        ensemble_path = os.path.join(folder_path, ensemble, 'Annual', 'oijl')                
        # Print ensemble for progress checking
        print('ensemble:',ensemble)
        years = []
        density = []
        # Iterate on files
        for file in os.listdir(ensemble_path):
            file_path = os.path.join(ensemble_path, file)
            # Processing on each file
            if os.path.isfile(file_path):
                # Get year
                start_time = time.time()
                year = file[3:7]
                print(year)
                years.append(year)
                # Get data, make an nc object, do process of choice with data and close the nc object
                # If needed arrays already saved, get those
                # Otherwise, access arrays and save them
                den_filename = ensemble_path+'\\pot_dens\\'+year+'.nc'
                if os.path.exists(den_filename):
                    temp = nc.Dataset(den_filename, mode='r')

                    den = temp.variables['pot_dens']
                else:
                    data = nc.Dataset(file_path, mode='r')
                    den = data.variables['pot_dens'] #[depth][lat][long]
                    save_array(ensemble_path,den,['pot_dens',year])
                    
                area_filename = ensemble_path+'\\oxyp\\'+year+'.nc'
                if os.path.exists(area_filename):
                    area = nc.Dataset(area_filename, mode='r').variables['oxyp']
                else:
                    area = data.variables['oxyp3']
                    save_array(ensemble_path,area,['oxyp',year])
                # For averaging density, use get_density_region function in goddard library
                temp = gd.get_density_region(den,area,region)
                
                if 'data' in locals():
                    data.close()
                else:
                    None
                density.append(temp)
                end_time = time.time()
                execution_time = end_time - start_time
                tim+=execution_time
                #print(f"Time taken: {execution_time:.6f} seconds")
                # if year == '2015':
                #     break
        print('average time:', tim/385)        
        # Save the list as a pickle file
        with open(ensemble+'_den.pkl', 'wb') as file:
            pickle.dump(density, file)
        # Add entry for ensemble in dict, add years if its the first one
        temp_dict[ensemble] = density
        if 'Years' not in temp_dict.keys(): 
            temp_dict['Years'] = years
    # Make the od object
    output = pd.DataFrame(temp_dict)
    # File path for saving the CSV file
    filename = 'DENvsTIME_' + regions + '.csv'
    file_path = os.path.join(os.getcwd(), filename)
    
    # If file does not exist, make new csv with a starting sheet
    if os.path.exists(file_path):
        file = pd.ExcelFile(file_path)
        # Check if sheet name exists
        if depth in file.sheet_names:
            depth = depth+'_new'
        # Add data in new sheet in exisitng csv
        with pd.ExcelWriter(file_path, mode='a', engine='openpyxl') as writer:
            output.to_excel(writer, sheet_name=depth, index=False)
    else:
        output.to_csv(filename,index=False)
        writer = pd.ExcelWriter(file_path, engine='openpyxl')
        output.to_excel(writer, sheet_name = depth, index=False)
        writer.save()


folder_path = r"D:\\NetCDF Files"
den_from_local(folder_path)