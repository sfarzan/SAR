from os import walk
import serial
from kalman import KalmanFilter
import pandas as pd
from datetime import datetime
import csv
import math
import numpy as np

filepath = ''
DATA_ARRAY_SIZE = 15 # num samples per powLevel
NUM_POW_LEVELS = 15 #0-14 db scale from receiver


CSV_FILEPATH = '600cm_outdoor_5dm.csv'

def collection():
    """"
    takes X amount of samples and puts them into an array to later be filtered
    needs to be able to figure out what power level we are at?
    hmmmm
    data structure = {powLevel 0: [rssiVal], [timeStamp], 
                       powLevel 1: [rssiVal], [timeStamp]}
    open port
    """
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200)
    data_array = {}
   
    while ser.is_open: # port is open start collection
        data_message = ser.readline().decode('utf-8').strip() # this is the message
        if data_message: 
            #if something is received, read the message portion, based on what powlevel
            #put into corresponding dictionary

            #need a way to track what the first powLevel received was, so first powLevel
            #then end collection once that array is filled

            #all logic is based on keys and len of each list
            timeStamp = datetime.now().strftime("%m/%d/%H:%M:%S")
            data_message_filtered = data_message.split(',')
            powLevel = data_message_filtered[-3] 
            rssiVal = int(data_message_filtered[-2]) #was a str-->int
            
            if not data_array:
                # figure out what first powlevel read was
                first_powLevel = powLevel 
            

            if (powLevel == first_powLevel) and (len(data_array.keys())== NUM_POW_LEVELS):
                # if we are back at first_powLevel and previous powLevel is full 
                return data_array

            if powLevel in data_array:
                data_array[powLevel][0].append(rssiVal)
                data_array[powLevel][1].append(timeStamp)
            else:
                data_array[powLevel] = [[],[]]
                data_array[powLevel][0].append(rssiVal)
                data_array[powLevel][1].append(timeStamp)



def kalman_filter(data_points, process_noise, measurement_noise):
    
    # filtering portion takes data from collection, and applies filter
    # RSSI measurement with the lowest var, is the RSSI value used for heading
    
    kalman_dict = {}

    for key in data_points.keys():

        kf = KalmanFilter(process_noise, measurement_noise)
        """
        create a new KF for each power factor
        get all the rssi values, then create a similar structured
        to data_array dict
        
        data_points = {powLevel: [kf_rssi], [variance]}

        """
        raw_array = list(data_points[key].values())
        for i in range(len(raw_array)):
            kalman_dict[key][0] = kf.filter(raw_array[i])
            kalman_dict[key][1] - kf.get_cov()
        print("Data Points\n", data_points, "Kalman dict", kalman_dict)

        return data_points, kalman_dict
    """
    old code
     
    rssi_array = [0] * DATA_ARRAY_SIZE
    variance_array = [0] * DATA_ARRAY_SIZE
    raw_array = list(data_points.values())
    rssi_array = [0] * DATA_ARRAY_SIZE
    variance_array = [0] * DATA_ARRAY_SIZE
    kalman_dict = {}
    for i in range(len(data_points)):
        kalman_dict[rssi_array[i]] = variance_array[i]
        print("Data point", raw_array[i], "filtered value", rssi_array[i], "variance", variance_array[i])
    
    print(kalman_dict)
    write_to_csv(data_points, kalman_dict)
    min_variance_index = min(enumerate(variance_array), key=lambda x: x[1])[0]
    return rssi_array[min_variance_index], variance_array[min_variance_index]
    """

def write_to_csv(original_data, kalman_dict):
    with open(CSV_FILEPATH, 'w', newline='') as csvfile:
        fieldnames = ['Time', 'Pow Level', 'Original Value', 'KF value', 'Variance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        var_list = list(kalman_dict.values())
        kf_list = list(kalman_dict.keys())
        powLevel_list = list(original_data.keys())

        writer.writeheader()
        for i, (time_stamp, original_value) in enumerate(original_data.items()):
            kalman_value = kf_list[i]
            variance = var_list[i]
            writer.writerow({'Time': time_stamp, 'Original Value': original_value, 'KF value': kalman_value, 'Variance': variance})
## May 7 testing
data_points = collection()
kalman_filter(data_points, .008, .1)
