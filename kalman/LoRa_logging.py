from os import walk
import serial
from kalman import KalmanFilter
import pandas as pd
from datetime import datetime
import csv
import math


filepath = ''
DATA_ARRAY_SIZE = 9
CSV_FILEPATH = 'data.csv'

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
    d = 10**((A - RSSI + X) / (10 * n))
    return d

def trilateration(drone1_lat, drone1_lon, drone1_rssi, drone2_lat, drone2_lon, drone2_rssi, drone3_lat, drone3_lon, drone3_rssi):
    # provides GPS estimate, use this and leaders position to generate heading for swarm

    A = 2 * drone2_lat - 2 * drone1_lat
    B = 2 * drone2_lon - 2 * drone1_lon
    C = drone1_rssi ** 2 - drone2_rssi ** 2 - drone1_lat ** 2 + drone2_lat ** 2 - drone1_lon ** 2 + drone2_lon ** 2
    D = 2 * drone3_lat - 2 * drone2_lat
    E = 2 * drone3_lon - 2 * drone2_lon
    F = drone2_rssi ** 2 - drone3_rssi ** 2 - drone2_lat ** 2 + drone3_lat ** 2 - drone2_lon ** 2 + drone3_lon ** 2
    estimate_lat = (C * E - F * B) / (E * A - B * D)
    estimate_lon = (C * D - A * F) / (B * D - A * E)
    return estimate_lat, estimate_lon

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

# Example usage
drone1_lat, drone1_lon = 51.5074, -0.0278
estimate_lat, estimate_lon = 51.5194, -0.0129

heading_result = heading(drone1_lat, drone1_lon, estimate_lat, estimate_lon)
print("Heading:", heading_result)

# data_points = collection()
# kalman_filter(data_points, .008, .1)
# exportExcel('data.xlsx', rssi_array, variance_array)

# data_points = collection()
# kalman_filter(data_points, .008, .1)

print(rssi_to_meters(49))
