import serial
from kalman import KalmanFilter
import pandas as pd
from datetime import datetime
import csv



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
    write_to_csv(data_points, kalman_dict)
    min_variance_index = min(enumerate(variance_array), key=lambda x: x[1])[0]
    return rssi_array[min_variance_index], variance_array[min_variance_index]

def write_to_csv(original_data, kalman_dict):
    with open(CSV_FILEPATH, 'w', newline='') as csvfile:
        fieldnames = ['Time', 'Original Value', 'Kalman Filtered Value', 'Variance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for time_stamp, original_value in original_data.items():
           # kalman_value = kalman_dict.get(original_value, '')  # Get the Kalman filtered value for the original value
            # variance = kalman_dict.get(original_value, '')  # Get the variance for the original value
            # kalman_value = next((k for k, v in kalman_dict.items() if v == original_value), '')  # Get the key from kalman_dict where value equals original_value
            writer.writerow({'Time': time_stamp, 'Original Value': original_value, 'Kalman Filtered Value': kalman_value, 'Variance': variance})
        
        for key, value in kalman_dict.items():
            writer.writerow({'KF Val' : key, 'Var' : value})

# Example usage
# lora_init()
# data_points = collection()
# kalman_filter(data_points, .008, .1)
# exportExcel('data.xlsx', rssi_array, variance_array)

data_points = collection()
kalman_filter(data_points, .008, .1)
