import csv
import matplotlib.pyplot as plt

# File path for the CSV file
filename = 'AMOCvsTIME_lat26.csv'

# Lists to store the data
x = []
y = []

# Read data from the CSV file
with open(filename, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row

    for row in reader:
        x.append(float(row[0]))
        y.append(float(row[1]))

# Create a figure and axes
fig, ax = plt.subplots()

# Plot the data
ax.plot(x, y, marker='x',markersize=1)

# Customize the plot
ax.set_xlabel('Years')
ax.set_ylabel('AMOC')
ax.set_title('AMOC vs. Time')

# Display the plot
plt.show()
