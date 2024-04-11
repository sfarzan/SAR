import serial
from kalman import KalmanFilter

# I think we may want to open the serial port everytime we want to get measurements 
# but not continously, if we want to use other ports, but they might have different protocols

DATA_ARRAY_SIZE = 9
def lora_init():
    # should add code for setting up parameters of LoRa
    # address, network ID, what standard message is? 
    # need logic in case lose connection
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200)
    if ser.is_open:
        return True
    else: 
        return False


def collection():
   # takes X amount of samples and puts them into an array to later be filtered
    
   #open port
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200)
    data_array = DATA_ARRAY_SIZE * []
    while ser.is_open: # port is open start collection
        line = ser.readline().decode('utf-8').strip() # this is the message
        while len(data_array) != DATA_ARRAY_SIZE:
            data_array.append(line)
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

testData = [66,64,63,63,63,66,65,67,58]
print(kalman_filter(testData, .008, .1))

def trileration(x1, y1, r1, x2, y2, r2, x3, y3, r3):
    # provides GPS estimate, use this and leaders position to generate heading for swarm

    A = 2 * x2 - 2 * x1
    B = 2 * y2 - 2 * y1
    C = r1 ** 2 - r2 ** 2 - x1 ** 2 + x2 ** 2 - y1 ** 2 + y2 ** 2
    D = 2 * x3 - 2 * x2
    E = 2 * y3 - 2 * y2
    F = r2 ** 2 - r3 ** 2 - x2 ** 2 + x3 ** 2 - y2 ** 2 + y3 ** 2
    x = (C * E - F * B) / (E * A - B * D)
    y = (C * D - A * F) / (B * D - A * E)
    return x, y

