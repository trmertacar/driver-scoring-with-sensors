import csv
from math import radians, sin, cos, acos

# Constants for Earth's radius in kilometers and miles
R_KM = 6371
R_MILES = 3959

# Open the CSV file and read the lat, long points
with open('06-01-2023T06-49-58.csv', 'r') as f:
    reader = csv.reader(f)
    points = [(int(row[0]), float(row[1]), float(row[2])) for row in reader]

# Calculate the distance between each pair of points
for i in range(len(points) - 1):
    seconds1, lat1, long1 = points[i]
    seconds2, lat2, long2 = points[i + 1]

    # Convert lat, long to radians
    lat1 = radians(lat1)
    long1 = radians(long1)
    lat2 = radians(lat2)
    long2 = radians(long2)

    # Calculate distance using haversine formula
    distance = R_KM * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(long1 - long2))
    speed = 0
    if seconds2 != seconds1:
        speed = distance * 3600 / (seconds2 - seconds1)

    print(f'Distance between points {i} and {i + 1}: {speed} kilometers')
