import serial

ser = serial.Serial('/dev/serial0', baudrate = 115200)

i = 0
if ser.is_open:
    print('connection established')

else: 
    print('failure')

while ser.is_open:
    line = ser.readline().decode('utf-8').strip()

    if line:
        if i < 100:
            print(line)
            i += 1
