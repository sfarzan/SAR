import asyncio
from kalman import KalmanFilter
import math 
import numpy as np
import serial

# buffer which other portions of the code will access
rawBuffer = asyncio.Queue()
kfBuffer = asyncio.Queue()
varBuffer = asyncio.Queue()

processNoise = .08
measurementNoise = .1
async def get_rssi():
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200)
    kf = KalmanFilter(processNoise, measurementNoise)
    while ser.is_open:
        # decode the message        
        data_message = ser.readline().decode('utf-8').strip() # this is the message
        if data_message:
            data_message_filter = data_message.split(',')
            rssiVal = data_message_filter[-2]
            KF_rssi = kf.filter(rssiVal)
            KF_var = kf.get_cov()

            # fill the buffers
            await rawBuffer.put(rssiVal)
            await kfBuffer.put(KF_rssi)
            await varBuffer.put(KF_var)


async def gpsEstimate(drone1_lat, drone1_lon, drone1_dist,
                      drone2_lat, drone2_lon, drone2_dist,
                      drone3_lat, drone3_lon, drone3_dist):

    A = 2 * (drone2_lat - drone1_lat)
    B = 2 * (drone2_lon - drone1_lon)


    C = (drone1_dist / (111111 * np.cos(np.radians(drone1_lon))))**2 - (drone2_dist / (111111 * np.cos(np.radians(drone2_lon))))**2 - drone1_dist**2 + drone2_dist**2 - drone1_lon**2 + drone2_lon**2
    D = 2 * (drone3_lat - drone2_lat)
    E = 2 * (drone3_lon - drone2_lon)
    F = (drone2_dist / (111111 * np.cos(np.radians(drone2_lon))))**2 - (drone3_dist / (111111 * np.cos(np.radians(drone3_lon))))**2 - drone2_lat**2 + drone3_lat**2 - drone2_lon**2 + drone3_lon**2
    gpsEstimate_lat = (C * E - F * B) / (E * A - B * D)
    gpsEstimate_lon = (C * D - A * F) / (B * D - A * E)
    return gpsEstimate_lat, gpsEstimate_lon


def calculate_heading(leader_lat, leader_lon, gpsEstimate_lat, gpsEstimate_lon):
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
    leader_lat_rad = math.radians(leader_lat)
    leader_lon_rad = math.radians(leader_lon)
    gpsEstimate_lat_rad = math.radians(gpsEstimate_lat)
    gpsEstimate_lon_rad = math.radians(gpsEstimate_lon)
    
    # Calculate the bearing from the drone to the beacon
    y = math.sin(gpsEstimate_lon_rad - leader_lon_rad) * math.cos(gpsEstimate_lat_rad)
    x = math.cos(leader_lat_rad) * math.sin(gpsEstimate_lat_rad) - \
        math.sin(leader_lat_rad) * math.cos(gpsEstimate_lat_rad) * math.cos(gpsEstimate_lon_rad - leader_lon_rad)
    bearing = math.atan2(y, x)
    
    # Convert bearing to degrees and normalize to the range [0, 360)
    heading = math.degrees(bearing)
    if heading < 0:
        heading += 360
    
    return heading































































