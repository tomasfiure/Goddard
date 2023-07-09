import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# File path for the CSV files
den_filename = 'DENvsTIME.csv'
amoc_filename = 'AMOCvsTIME_lat48AllEnsembles.csv'

# Read data from the CSV file
den_data = pd.read_csv(den_filename)
amoc_data = pd.read_csv(amoc_filename)

# Get data
years = den_data.iloc[:,0]
density = den_data.iloc[:,[1,2,3,4]]
amoc = amoc_data.iloc[:,[1,2,3,4]]

# Function to plot amoc expressed as the difference between a years amoc and the first 10 years' average
def plot_delta_amoc_vs_density(density,amoc):
    #Get first 10-year average
    #d10_avg = [np.mean(density[col][:10])for col in density.columns]
    d10_avg = {col:np.mean(density[col][:10])for col in density.columns}
    a10_avg = {col:np.mean(amoc[col][:10])for col in amoc.columns}
    
    # Get data to plot
    delta_density= {col:density[col] - np.full(len(density),d10_avg[col]) for col in density.columns}
    delta_amoc= {col:amoc[col] - np.full(len(amoc),a10_avg[col]) for col in amoc.columns}
    
    # Calculate the coefficients of the polynomial fit
    coefficients = {col:np.polyfit(delta_density[col],delta_amoc[col],1) for col in density.columns}
    
    # Get estimated Gamma
    slope = {col: coefficients[col][0] for col in density.columns}
    print("Gamma:",slope)
    
    # Find correlation coefficient
    correlation_coefficients = {col:np.corrcoef(delta_density[col],delta_amoc[col])[0,1] for col in density.columns}
    print("correlation coefficients:",correlation_coefficients)
    
    # Generate the line of best fit
    line_of_best_fit = {col: np.polyval(coefficients[col], delta_density[col]) for col in density.columns}
    
    # Find Corrrelation Coefficient for Squared Realtion
    coefficients2 = {col:np.polyfit(delta_density[col],delta_amoc[col],2) for col in density.columns}  
    predicted_y = {col:np.polyval(coefficients2[col], delta_density[col]) for col in density.columns}
    correlation_coefficient2 = {col : np.corrcoef(delta_amoc[col], predicted_y[col])[0,1] for col in density.columns}
    print("correlation coefficient squared:",correlation_coefficient2)
    
    # Plot making and display
    # Notable Ranges: [2015:2100] = [:85],[2101:2200] = [85:185],[2201:2300] = [185:285], [2301:2400] = [285:385]
    colors = {'SSP245a':'blue', 'SSP245c':'red', 'SSP245g':'green', 'SSP245i':'orange'}
    
    for col in density.columns:
        plt.figure()
        plt.scatter(delta_density[col],delta_amoc[col],label = col, s=10,color = colors[col])
        plt.plot(delta_density[col],line_of_best_fit[col],color='black', label='Line of Best Fit')
        plt.xlabel('delta_density (kg/$m^3$)')
        plt.ylabel('delta_amoc (Sv)')
        plt.title(col)
        plt.legend()
        plt.show()

# Function call to run the plotting function    
#plot_delta_amoc_vs_density(density, amoc)

# Function to plot density against time 
def plot_density_vs_time(years,density):
    colors = {'SSP245a':'blue', 'SSP245c':'red', 'SSP245g':'green', 'SSP245i':'orange'}
    plt.figure()
    for col in density.columns:
        plt.plot(years,density[col],label = col,color = colors[col])
    plt.xlabel('Time (Year)')
    plt.ylabel('Density (kg/$m^3$)')
    plt.title("Density vs. Time")
    plt.legend()
    plt.show()     

# Function call to run plotting function
#plot_density_vs_time(years, density)