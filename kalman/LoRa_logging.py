from os import walk
import serial
from kalman import KalmanFilter
import pandas as pd
from datetime import datetime
import csv
import math
import numpy as np

filepath = ''
DATA_ARRAY_SIZE = 9
CSV_FILEPATH = 'data.csv'

# 35.3005451, longitude_deg: -120.66185949999999 drone 2 data


#latitude_deg: 35.3005578, longitude_deg: -120.66179249999999, drone 3

#latitude_deg: 35.3005208, longitude_deg: -120.6617909, drone1
drone2_lat = 35.3005451
drone2_lon = -120.66185949999
drone2_rssi_table = -68 
drone2_rssi_door = -60 # pretty consistent
drone2_rssi_cubesat = -68 # -72 
drone3_lat = 35.3005578
drone3_lon = -120.6617924999
drone3_rssi_table = -61 # pretty consistent 
drone3_rssi_door = -63
drone3_rssi_cubesat = -60
drone1_lat = 35.3005208
drone1_lon = -120.6617909
drone1_rssi_table = -61
drone1_rssi_door = -53
drone1_rssi_cubesat = -52



d1_dist_truth_DOOR = 2.9
d1_dist_truth_TABLE = 3.16
d1_dist_truth_CUBESAT = 8.3

d2_dist_truth_DOOR = 7.78
d2_dist_truth_TABLE = 2.93
d2_dist_truth_CUBESAT = 7.32

d3_dist_truth_DOOR = 6.49
d3_dist_truth_TABLE = 3.74
d3_dist_truth_CUBESAT = 5.15
def collection():
   # takes X amount of samples and puts them into an array to later be filtered
    
   #open port
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200)
    data_array = {}
    samples = 0
    while ser.is_open: # port is open start collection
        data_message = ser.readline().decode('utf-8').strip() # this is the message
        if samples < DATA_ARRAY_SIZE:
            # +RCV=50,5,HELLO,-43,47 this is what sample line  will look RSSI_Val
            data_message_filtered = data_message.split(',')
            
            time_stamp = datetime.now().strftime("%m/%d/%H:%M:%S")
            data_array[time_stamp] = int(data_message_filtered[-2]) #was a str-->int
            samples += 1
            print(f"Num of samples {samples} > {DATA_ARRAY_SIZE}")
        else:
            print(data_array)
            return data_array


def kalman_filter(data_points, process_noise, measurement_noise):
    
    # filtering portion takes data from collection, and applies filter
    # RSSI measurement with the lowest var, is the RSSI value used for heading
    kf = KalmanFilter(process_noise, measurement_noise)
    raw_array = list(data_points.values())
    rssi_array = [0] * DATA_ARRAY_SIZE
    variance_array = [0] * DATA_ARRAY_SIZE
    kalman_dict = {}
    for i in range(len(data_points)):
        rssi_array[i] = kf.filter(raw_array[i])
        variance_array[i] = kf.get_cov()
        kalman_dict[rssi_array[i]] = variance_array[i]
        print("Data point", raw_array[i], "filtered value", rssi_array[i], "variance", variance_array[i])
    
    print(kalman_dict)
    write_to_csv(data_points, kalman_dict)
    min_variance_index = min(enumerate(variance_array), key=lambda x: x[1])[0]
    return rssi_array[min_variance_index], variance_array[min_variance_index]

def write_to_csv(original_data, kalman_dict):
    with open(CSV_FILEPATH, 'w', newline='') as csvfile:
        fieldnames = ['Time', 'Original Value', 'Kalman Filtered Value', 'Variance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        var_list = list(kalman_dict.values())
        kf_list = list(kalman_dict.keys())
        print(kf_list)

        for i, (time_stamp, original_value) in enumerate(original_data.items()):
            # Get the Kalman filtered value from the original data
            kalman_value = kf_list[i]
            variance = var_list[i]
            writer.writerow({'Time': time_stamp, 'Original Value': original_value, 'Kalman Filtered Value': kalman_value, 'Variance': variance})

def rssi_to_meters(RSSI):
   # d is estimated distance in meters
   #     n is the calibrated path loss exponent
   #     A is calibrated received signal strength at 1 meter distance    
   #     n is calibrated path loss exponent
   #     x is shadowing factor
        
        
   
    A = 61 
    X = 0
    n = 2.7
    d = 10**((A + RSSI + X) / (10 * n))
    return d


def trilateration_transform(x1, y1, r1, x2, y2, r2, x3, y3, r3):
    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = (r1 / (111111 * np.cos(np.radians(y1))))**2 - (r2 / (111111 * np.cos(np.radians(y2))))**2 - x1**2 + x2**2 - y1**2 + y2**2
    D = 2 * (x3 - x2)
    E = 2 * (y3 - y2)
    F = (r2 / (111111 * np.cos(np.radians(y2))))**2 - (r3 / (111111 * np.cos(np.radians(y3))))**2 - x2**2 + x3**2 - y2**2 + y3**2
    x = (C * E - F * B) / (E * A - B * D)
    y = (C * D - A * F) / (B * D - A * E)
    return x, y

def heading(drone1_lat, drone1_lon, estimate_lat, estimate_lon):
    # Convert latitude and longitude from degrees to radians
    drone1_lat, drone1_lon, estimate_lat, estimate_lon = map(math.radians, [drone1_lat, drone1_lon, estimate_lat, estimate_lon])

    # Calculate the difference in longitude
    delta_lon = estimate_lon - drone1_lon

    # Calculate the difference in latitude
    delta_lat = estimate_lat - drone1_lat

    # Calculate the heading in radians
    heading_rad = math.atan2(math.sin(delta_lat) * math.cos(estimate_lat), math.cos(drone1_lat) * math.sin(estimate_lat) - math.sin(drone1_lat) * math.cos(estimate_lat) * math.cos(delta_lon))

    # Convert the heading from radians to degrees
    heading_deg = math.degrees(heading_rad)

    return heading_deg

def calculate_heading(drone_lat, drone_lon, beacon_lat, beacon_lon):
    """
    Calculates the heading from the drone to the beacon.
    
    Args:
        drone_lat (float): The latitude of the drone's position.
        drone_lon (float): The longitude of the drone's position.
        beacon_lat (float): The latitude of the beacon's position.
        beacon_lon (float): The longitude of the beacon's position.
    
    Returns:
        float: The heading from the drone to the beacon, in degrees.
    """
    # Convert latitude and longitude to radians
    drone_lat_rad = math.radians(drone_lat)
    drone_lon_rad = math.radians(drone_lon)
    beacon_lat_rad = math.radians(beacon_lat)
    beacon_lon_rad = math.radians(beacon_lon)
    
    # Calculate the bearing from the drone to the beacon
    y = math.sin(beacon_lon_rad - drone_lon_rad) * math.cos(beacon_lat_rad)
    x = math.cos(drone_lat_rad) * math.sin(beacon_lat_rad) - \
        math.sin(drone_lat_rad) * math.cos(beacon_lat_rad) * math.cos(beacon_lon_rad - drone_lon_rad)
    bearing = math.atan2(y, x)
    
    # Convert bearing to degrees and normalize to the range [0, 360)
    heading = math.degrees(bearing)
    if heading < 0:
        heading += 360
    
    return heading
# Convert latitude and longitude to Cartesian coordinates

# Calculate distances from RSSI values
drone1_dist = rssi_to_meters(drone1_rssi_door)
drone2_dist = rssi_to_meters(drone2_rssi_door)
drone3_dist = rssi_to_meters(drone3_rssi_door)

# Call the trilateration function
estimate_x, estimate_y = trilateration_transform(drone1_lat, drone1_lon, d1_dist_truth_TABLE, drone2_lat, drone2_lon, d2_dist_truth_TABLE, drone3_lat, drone3_lon, d3_dist_truth_TABLE)

print("updated results table __________________")
print(estimate_x, estimate_y)
print(heading(drone1_lat, drone1_lon, estimate_x, estimate_y))
print(calculate_heading(drone1_lat, drone1_lon, estimate_x,estimate_y))
print("results_______________")
#
estimate_x_door, estimate_y_door = trilateration_transform(drone1_lat, drone1_lon, d1_dist_truth_DOOR, drone2_lat, drone2_lon, d2_dist_truth_DOOR, drone3_lat, drone3_lon, d3_dist_truth_DOOR)

print("updated results DOOR __________________")
print(estimate_x_door, estimate_y_door)
print(heading(drone1_lat, drone1_lon, estimate_x_door, estimate_y_door))
print(calculate_heading(drone1_lat, drone1_lon, estimate_x_door, estimate_y_door))
print("results_______________")
#
estimate_x_CUBESAT, estimate_y_CUBESAT = trilateration_transform(drone1_lat, drone1_lon, d1_dist_truth_CUBESAT, drone2_lat, drone2_lon, d2_dist_truth_CUBESAT, drone3_lat, drone3_lon, d3_dist_truth_CUBESAT)

print("updated results CUBESAT__________________")
print(estimate_x_CUBESAT, estimate_y_CUBESAT)
print(heading(drone1_lat, drone1_lon, estimate_x_CUBESAT, estimate_y_CUBESAT))
print(calculate_heading(drone1_lat,drone1_lon, estimate_x_CUBESAT, estimate_y_CUBESAT))
print("results_______________")
#
# # Example usage
# drone1_lat, drone1_lon = 51.5074, -0.0278
# estimate_lat, estimate_lon = 51.5194, -0.0129

# heading_result = heading(drone1_lat, drone1_lon, estimate_lat, estimate_lon)
# print("Heading:", heading_result)

# data_points = collection()
# kalman_filter(data_points, .008, .1)
# exportExcel('data.xlsx', rssi_array, variance_array)

# data_points = collection()
# kalman_filter(data_points, .008, .1)

# print(rssi_to_meters(49))
#
cubesat_meter_drone1 = rssi_to_meters(drone1_rssi_cubesat)
table_meter_drone1 = rssi_to_meters(drone1_rssi_table)
door_meter_drone1 = rssi_to_meters(drone1_rssi_door)
print(drone1_rssi_table)
print(f" table meters drone{table_meter_drone1}")

cubesat_meter_drone2 = rssi_to_meters(drone2_rssi_cubesat)
table_meter_drone2 = rssi_to_meters(drone2_rssi_table)
door_meter_drone2 = rssi_to_meters(drone2_rssi_door)
print(drone2_rssi_table)
print(f"table meters drone2 {table_meter_drone2}")

cubesat_meter_drone3 = rssi_to_meters(drone3_rssi_cubesat)
table_meter_drone3 = rssi_to_meters(drone3_rssi_table)
door_meter_drone3 = rssi_to_meters(drone3_rssi_door)
print(drone3_rssi_table)
print(f"table_meter_drone3 {table_meter_drone3}")
#
# print(drone3_rssi_cubesat)
# print(cubesat_meter_drone3)
#
#
# print("------------------")
# print(f"d1 dist {d1_dist_truth_DOOR}, d2 dist {d2_dist_truth_DOOR} d3 dist {d3_dist_truth_DOOR}")
# estimate_lat_truth, estimate_lon_truth = trilateration(drone1_lat, drone1_lon, d1_dist_truth_DOOR, drone2_lat, drone2_lon, d2_dist_truth_DOOR,
#                                                      drone3_lat, drone3_lon, d3_dist_truth_DOOR)
# #
# # estimate_lat_rssi, estimate_lon_rssi = trilateration(drone1_lat, drone1_lon, table_meter_drone1, drone2_lat, drone2_lon,
# #                                            table_meter_drone2, drone3_lat, drone3_lon, table_meter_drone3)
#
# print(estimate_lat_truth, estimate_lon_truth)
# print(heading(drone1_lat, drone1_lon, estimate_lat_truth, estimate_lon_truth))
#
#
# #
# # estimate_lat_truth2, estimate_lon_truth2 = trilateration(drone1_lat, drone1_lon, d1_dist_truth_TABLE, drone2_lat, drone2_lon, d2_dist_truth_TABLE,
# #                                                          drone3_lat, drone3_lon, d2_dist_truth_TABLE)
# #
# # print(estimate_lat_truth2, estimate_lon_truth2)
# # print(heading(drone1_lat, drone1_lon, estimate_lat_truth2, estimate_lon_truth2))
# # print(estimate_lat, estimate_lon)
