import serial
from kalman import KalmanFilter
import pandas as pd
from datetime import datetime

from kalman.heading_control import lora_init


filepath = ''
DATA_ARRAY_SIZE = 9
def collection():
   # takes X amount of samples and puts them into an array to later be filtered
    
   #open port
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200)
    data_array = {}
    while ser.is_open: # port is open start collection
        data_message = ser.readline().decode('utf-8').strip() # this is the message
        while len(data_array) != DATA_ARRAY_SIZE:
            # +RCV=50,5,HELLO,-43,47 this is what sample line  will look RSSI_Val
            data_message = data_message.split(',')
            print(data_message)
            time_stamp = datetime.now()
            data_array[time_stamp] = RSSI_val
        else:
            return data_array


def kalman_filter(data_points, process_noise, measurement_noise):
    
    # filtering portion takes data from collection, and applies filter
    # RSSI measurement with the lowest var, is the RSSI value used for heading
    kf = KalmanFilter(process_noise, measurement_noise)

    rssi_array = [0] * DATA_ARRAY_SIZE
    variance_array = [0] * DATA_ARRAY_SIZE

    for i in range(len(data_points)):
        rssi_array[i] = kf.filter(data_points[i])
        variance_array[i] = kf.get_cov()
        print("Data point", data_points[i], "filtered value", rssi_array[i], "variance", variance_array[i])

    min_variance_index = min(enumerate(variance_array), key=lambda x: x[1])[0]
    return rssi_array[min_variance_index], variance_array[min_variance_index]

    

def exportExcel(filepath, rssi_array, variance_array):
    # Create a DataFrame with timestamps, RSSI values, and variances
    df = pd.DataFrame({
        'Timestamp': [datetime.now()] * len(rssi_array),
        'RSSI': rssi_array,
        'Variance': variance_array
    })

    # Export DataFrame to Excel
    df.to_excel(filepath, index=False)

# Example usage
# lora_init()
# data_points = collection()
# kalman_filter(data_points, .008, .1)
# exportExcel('data.xlsx', rssi_array, variance_array)

collection()
